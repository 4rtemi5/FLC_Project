import warnings

from llvmlite import ir

i32 = ir.IntType(32)
i1 = ir.IntType(1)
f64 = ir.DoubleType()

_var_symtab = {}
_types = [ir.VoidType(), ir.IntType(1), ir.IntType(32), ir.DoubleType()]


class CodegenError(Exception):
    pass


class CastWarning(Warning):
    pass


class Number:
    def __init__(self, builder, printf, module, value):
        self.builder = builder
        self.module = module
        self.printf = printf
        self.token = value

    def eval(self):
        if '.' in self.token.value:
            i = ir.Constant(ir.DoubleType(), float(self.token.value))
        else:
            i = ir.Constant(ir.IntType(32), int(self.token.value))

        return i


# class String:
#     def __init__(self, builder, printf, module, token):
#         self.builder = builder
#         self.printf = printf
#         self.module = module
#         self.token = token
#
#     def eval(self):
#         if len(self.token.value) <= 2:
#             return None
#         b = bytearray(str(self.token.value).strip('"').encode('utf8'))
#
#         s_bytes = ir.Constant(ir.ArrayType(ir.IntType(8), len(b)), b)
#         return s_bytes


class UnaryOp:
    def __init__(self, builder, module, value):
        self.builder = builder
        self.module = module
        self.value = value


class Neg(UnaryOp):
    def eval(self):
        val = self.value.eval()
        if val.type == f64:
            i = self.builder.fsub(ir.Constant(val.type, 0.0), val)
        else:
            i = self.builder.sub(ir.Constant(val.type, 0), val)
        return i


class BinaryOp:
    def __init__(self, builder, module, left, right):
        self.builder = builder
        self.module = module
        self.left = left
        self.right = right

    def convert(self, value):
        if value.type == i32:
            return self.builder.sitofp(value, ir.DoubleType())
        return value


class Sum(BinaryOp):
    def eval(self):
        left = self.left.eval()
        right = self.right.eval()
        if left.type == i32 and right.type == i32:
            return self.builder.add(left, right)
        return self.builder.fadd(self.convert(left), self.convert(right))


class Sub(BinaryOp):
    def eval(self):
        left = self.left.eval()
        right = self.right.eval()
        if left.type == i32 and right.type == i32:
            return self.builder.sub(left, right)
        i = self.builder.fsub(self.convert(left), self.convert(right))
        return i


class Mul(BinaryOp):
    def eval(self):
        left = self.left.eval()
        right = self.right.eval()
        if left.type == i32 and right.type == i32:
            return self.builder.mul(left, right)
        i = self.builder.fmul(self.convert(left),
                              self.convert(right))
        return i


class Div(BinaryOp):
    def eval(self):
        i = self.builder.sdiv(self.convert(self.left.eval()),
                              self.convert(self.right.eval()))
        return i


class Comparison:
    def __init__(self, builder, printf, module, left, right, operation):
        self.builder = builder
        self.module = module
        self.printf = printf
        self.left = left
        self.right = right
        self.operation = operation

    def convert(self, value):
        if value.type == i32:
            return self.builder.sitofp(value, ir.DoubleType())
        return value

    def eval(self):
        if self.operation in ['<', '<=', '==', '!=', '>=', '>']:
            tf = self.builder.fcmp_unordered(self.operation,
                                             self.convert(self.left.eval()),
                                             self.convert(self.right.eval()))
            return tf
        else:
            raise CodegenError('Invalid comparison operator "%s"' % self.operation)


class VariableInstance:

    def __init__(self, builder, module, printf, name, value=None):
        self.name = name
        self.value = value
        self.builder = builder
        self.module = module
        self.printf = printf

    def _alloca(self, val_type, name):
        """Create an alloca in the entry BB of the current function."""
        with self.builder.goto_entry_block():
            alloca = self.builder.alloca(val_type, size=None, name=name)
        return alloca

    def eval(self):
        if self.value is not None:
            set_val = self.value.eval()
        else:
            set_val = ir.Constant(ir.VoidType(), 0)
        typ = set_val.type
        ptr_addr = None
        if self.name in _var_symtab:
            ptr_addr, old_typ = _var_symtab[self.name]
            if typ != old_typ:
                warnings.warn('Implicit typecasting might break stuff!', CastWarning)
                if old_typ in [i1, i32]:
                    set_val = self.builder.fptosi(set_val, old_typ)
                else:
                    set_val = self.builder.sitofp(set_val, old_typ)
        if ptr_addr is None:
            ptr_addr = self._alloca(typ, self.name + '_' + str(typ))
        self.builder.store(set_val, ptr_addr)
        _var_symtab[self.name] = [ptr_addr, typ]


class Variable:

    def __init__(self, builder, module, printf, name):
        self.name = name
        self.builder = builder
        self.module = module
        self.printf = printf

    def eval(self):
        if self.name in _var_symtab:
            ptr_addr, typ = _var_symtab[self.name]
        else:
            raise CodegenError("Undefined variable: " + self.name)
        val = self.builder.load(ptr_addr, self.name + '_' + str(typ))
        return val


class IfElse:
    def __init__(self, builder, module, condition, if_body, else_body=None):
        self.builder = builder
        self.module = module
        self.condition = condition
        self.if_body = if_body
        self.else_body = else_body

    def eval(self):
        with self.builder.if_else(self.condition.eval()) as (then, otherwise):
            with then:
                for s in self.if_body:
                    if s is not None:
                        s.eval()
            with otherwise:
                if self.else_body is not None:
                    for s in self.else_body:
                        if s is not None:
                            s.eval()


class While:
    def __init__(self, builder, module, condition, body):
        self.builder = builder
        self.module = module
        self.condition = condition
        self.body = body
        self.body_block = self.builder.append_basic_block("w_body")
        self.after_block = self.builder.append_basic_block("w_after")

    def eval(self):
        self.builder.cbranch(self.condition.eval(), self.body_block, self.after_block)
        self.builder.position_at_start(self.body_block)
        for b in self.body:
            b.eval()
        self.builder.cbranch(self.condition.eval(), self.body_block, self.after_block)
        ret = self.builder.position_at_start(self.after_block)
        return ret


class Print:
    counter = 0

    def __init__(self, builder, module, printf, value):
        self.builder = builder
        self.module = module
        self.printf = printf
        self.value = value
        Print.counter += 1
        self.instance = Print.counter

    def convert_to_string(self, ir_object):
        if ir_object.type == f64:
            fn = self.builder.module.globals.get('floatToString')
            return self.builder.call(fn, [ir_object])
        elif ir_object.type in [i1, i32]:
            fn = self.builder.module.globals.get('intToString')
            return self.builder.call(fn, [ir_object])
        else:
            return ir_object

    def eval(self):
        value = self.value.eval()

        # declare format
        if value.type is f64:
            fmt = "%f \n\0"
        elif value.type in [i1, i32]:
            fmt = "%i \n\0"
        else:
            fmt = "%s \n\0"

        # Declare argument list
        voidptr_ty = ir.IntType(8).as_pointer()
        c_fmt = ir.Constant(ir.ArrayType(ir.IntType(8), len(fmt)),
                            bytearray(fmt.encode("utf8")))
        global_fmt = ir.GlobalVariable(self.module, c_fmt.type, name="fstr%s" % self.instance)
        global_fmt.linkage = 'internal'
        global_fmt.global_constant = True
        global_fmt.initializer = c_fmt
        fmt_arg = self.builder.bitcast(global_fmt, voidptr_ty)

        # Call Print Function
        self.builder.call(self.printf, [fmt_arg, value])


class MainFunction:
    def __init__(self, builder, module, printf, body):
        self.builder = builder
        self.module = module
        self.printf = printf
        self.body = body

    def eval(self):
        for block in self.body:
            if block is not None:
                block.eval()
