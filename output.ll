; ModuleID = "/home/raf/Dev/CompilersProject/Compilers_Project (final)/codegen.py"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

define void @"main"() 
{
entry:
  %".2" = sitofp i32 13 to double
  %".3" = fadd double 0x4028000000000000, %".2"
  %".4" = sitofp i32 15 to double
  %".5" = fadd double %".3", %".4"
  %".6" = bitcast [5 x i8]* @"fstr1" to i8*
  %".7" = call i32 (i8*, ...) @"printf"(i8* %".6", double %".5")
  %".8" = sitofp i32 2 to double
  %".9" = sitofp i32 0 to double
  %".10" = fcmp ugt double %".8", %".9"
  %".11" = bitcast [5 x i8]* @"fstr2" to i8*
  %".12" = call i32 (i8*, ...) @"printf"(i8* %".11", i1 %".10")
  %"im_so_cool_i32" = alloca i32
  store i32 1, i32* %"im_so_cool_i32"
  %"im_so_cool_i32.1" = load i32, i32* %"im_so_cool_i32"
  %".14" = sub i32 0, %"im_so_cool_i32.1"
  %".15" = sub i32 0, 1
  %".16" = sub i32 %".14", %".15"
  %".17" = add i32 %".16", 1
  %".18" = bitcast [5 x i8]* @"fstr3" to i8*
  %".19" = call i32 (i8*, ...) @"printf"(i8* %".18", i32 %".17")
  %"im_so_cool_i32.2" = load i32, i32* %"im_so_cool_i32"
  %".20" = bitcast [5 x i8]* @"fstr4" to i8*
  %".21" = call i32 (i8*, ...) @"printf"(i8* %".20", i32 %"im_so_cool_i32.2")
  %".22" = sitofp i32 2 to double
  %".23" = sitofp i32 1 to double
  %".24" = fcmp ugt double %".22", %".23"
  %"loopvar_i32" = alloca i32
  br i1 %".24", label %"entry.if", label %"entry.else"
w_body:
  %"loopvar_i32.2" = load i32, i32* %"loopvar_i32"
  %".43" = bitcast [5 x i8]* @"fstr7" to i8*
  %".44" = call i32 (i8*, ...) @"printf"(i8* %".43", i32 %"loopvar_i32.2")
  %"loopvar_i32.3" = load i32, i32* %"loopvar_i32"
  %".45" = sub i32 %"loopvar_i32.3", 1
  store i32 %".45", i32* %"loopvar_i32"
  %"loopvar_i32.4" = load i32, i32* %"loopvar_i32"
  %".47" = sitofp i32 %"loopvar_i32.4" to double
  %".48" = sitofp i32 0 to double
  %".49" = fcmp ugt double %".47", %".48"
  br i1 %".49", label %"w_body", label %"w_after"
w_after:
  %"loopvar_i32.5" = load i32, i32* %"loopvar_i32"
  %".51" = bitcast [5 x i8]* @"fstr8" to i8*
  %".52" = call i32 (i8*, ...) @"printf"(i8* %".51", i32 %"loopvar_i32.5")
  ret void
entry.if:
  %".26" = sitofp i32 2 to double
  %".27" = sitofp i32 4 to double
  %".28" = fcmp ult double %".26", %".27"
  br i1 %".28", label %"entry.if.if", label %"entry.if.else"
entry.else:
  %".35" = bitcast [5 x i8]* @"fstr6" to i8*
  %".36" = call i32 (i8*, ...) @"printf"(i8* %".35", i32 100)
  br label %"entry.endif"
entry.endif:
  store i32 10, i32* %"loopvar_i32"
  %"loopvar_i32.1" = load i32, i32* %"loopvar_i32"
  %".39" = sitofp i32 %"loopvar_i32.1" to double
  %".40" = sitofp i32 0 to double
  %".41" = fcmp ugt double %".39", %".40"
  br i1 %".41", label %"w_body", label %"w_after"
entry.if.if:
  %".30" = bitcast [5 x i8]* @"fstr5" to i8*
  %".31" = call i32 (i8*, ...) @"printf"(i8* %".30", i32 11111)
  br label %"entry.if.endif"
entry.if.else:
  br label %"entry.if.endif"
entry.if.endif:
  br label %"entry.endif"
}

declare i32 @"printf"(i8* %".1", ...) 

@"fstr1" = internal constant [5 x i8] c"%f \0a\00"
@"fstr2" = internal constant [5 x i8] c"%i \0a\00"
@"fstr3" = internal constant [5 x i8] c"%i \0a\00"
@"fstr4" = internal constant [5 x i8] c"%i \0a\00"
@"fstr5" = internal constant [5 x i8] c"%i \0a\00"
@"fstr6" = internal constant [5 x i8] c"%i \0a\00"
@"fstr7" = internal constant [5 x i8] c"%i \0a\00"
@"fstr8" = internal constant [5 x i8] c"%i \0a\00"