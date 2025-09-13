import streamlit as st
import sympy as sp
from sympy.logic.boolalg import to_cnf, to_dnf, simplify_logic
from sympy.logic.inference import satisfiable
from z3 import (
    Bool, Implies as Z3Implies, And, Or, Not, Solver, sat, unsat,
    ForAll, Exists, Int, Function, DeclareSort, Const, BoolSort
)

# Page config
st.set_page_config(
    page_title="منطق گزاره‌ای و مرتبه اول",
    page_icon="🧠",
    layout="wide"
)

# App title and description
st.title("🧠 پیاده‌سازی منطق گزاره‌ای و منطق مرتبه اول")
st.markdown("""
این برنامه بر اساس کتاب هوش مصنوعی راسل و نوریگ پیاده‌سازی شده است و از کتابخانه‌های 
SymPy برای منطق گزاره‌ای و Z3 برای منطق مرتبه اول استفاده می‌کند.
""")

logic_type = st.sidebar.selectbox(
    "نوع منطق را انتخاب کنید:",
    ["معرفی", "منطق گزاره‌ای", "منطق مرتبه اول", "حل مسئله با kanren"]
)

if logic_type == "معرفی":
    st.header("معرفی پروژه")
    st.markdown("""
    ### ویژگی‌های برنامه
    - کار با منطق گزاره‌ای (Propositional Logic) با استفاده از SymPy
    - کار با منطق مرتبه اول (First-Order Logic) و حل استنتاج‌ها با Z3
    - بررسی ارضاپذیری، فرم‌های نرمال و استنتاج منطقی
    """)

elif logic_type == "منطق گزاره‌ای":
    st.header("منطق گزاره‌ای - SymPy")

    if 'formula_input' not in st.session_state:
        st.session_state.formula_input = "(P >> Q) & (Q >> R)"

    formula_input = st.text_input(
        "فرمول منطقی خود را وارد کنید:",
        value=st.session_state.formula_input,
        key="formula_input",
        help="از عملگرهای: & (و), | (یا), ~ (نفی), >> (استلزام) استفاده کنید"
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("تجزیه و تحلیل فرمول"):
            try:
                P, Q, R = sp.symbols('P Q R')
                expr = sp.sympify(st.session_state.formula_input, locals={'P': P, 'Q': Q, 'R': R})

                st.subheader("نتایج تجزیه و تحلیل:")
                st.write(f"**عبارت ورودی:**  `{expr}`")
                st.write(f"**فرم نرمال عطفی (CNF):**  `{to_cnf(expr)}`")
                st.write(f"**فرم نرمال فصلی (DNF):**  `{to_dnf(expr)}`")
                st.write(f"**فرم ساده شده:**  `{simplify_logic(expr)}`")

                sat_result = satisfiable(expr)
                st.write(f"**ارضاپذیری:** {sat_result if sat_result else 'ناسازگار'}")
            except Exception as e:
                st.error(f"خطا در پردازش فرمول: {e}")

    with col2:
        st.subheader("مثال‌های آماده")
        examples = [
            "P & Q",
            "P | Q",
            "P >> Q",
            "~(P & Q)",
            "(P >> Q) & (Q >> R)",
            "P & ~P"  # ناسازگار
        ]

        def load_example(example):
            st.session_state.formula_input = example

        for example in examples:
            st.button(f"بارگذاری: {example}", key=example, on_click=load_example, args=(example,))


elif logic_type == "منطق مرتبه اول":
    st.header("منطق مرتبه اول - ورودی سورها و تحلیل")

    col1, col2, col3 = st.columns(3)

    with col1:
        universal_input = st.text_area(
            "فرمول با سور جهانی (∀):",
            value="ForAll([x], Implies(P(x), Q(x)))",
            help="مثال: ForAll([x], Implies(P(x), Q(x)))",
            height=150
        )
        if st.button("تحلیل سور جهانی", key="universal_btn"):
            try:
                Human = DeclareSort('Human')
                x = Const('x', Human)
                P = Function('P', Human, BoolSort())
                Q = Function('Q', Human, BoolSort())

                formula = ForAll([x], Z3Implies(P(x), Q(x)))

                solver = Solver()
                solver.add(formula)
                result = solver.check()
                st.write(f"نتیجه حل (Universal): {result}")
                if result == sat:
                    model = solver.model()
                    model_dict = {}
                    for d in model.decls():
                        val = model[d]
                        try:
                            sort_name = val.sort().name()
                            if sort_name == 'Int':
                                model_dict[d.name()] = val.as_long()
                            else:
                                model_dict[d.name()] = str(val)
                        except AttributeError:
                            model_dict[d.name()] = str(val)
                    st.json(model_dict)
                else:
                    st.write("فرمول ناسازگار یا نامعین است.")
            except Exception as e:
                st.error(f"خطا: {e}")

    with col2:
        existential_input = st.text_area(
            "فرمول با سور وجودی (∃):",
            value="Exists([x], And(P(x), Q(x)))",
            help="مثال: Exists([x], And(P(x), Q(x)))",
            height=150
        )
        if st.button("تحلیل سور وجودی", key="existential_btn"):
            try:
                Human = DeclareSort('Human')
                x = Const('x', Human)
                P = Function('P', Human, BoolSort())
                Q = Function('Q', Human, BoolSort())

                formula = Exists([x], And(P(x), Q(x)))

                solver = Solver()
                solver.add(formula)
                result = solver.check()
                st.write(f"نتیجه حل (Existential): {result}")
                if result == sat:
                    model = solver.model()
                    model_dict = {}
                    for d in model.decls():
                        val = model[d]
                        try:
                            sort_name = val.sort().name()
                            if sort_name == 'Int':
                                model_dict[d.name()] = val.as_long()
                            else:
                                model_dict[d.name()] = str(val)
                        except AttributeError:
                            model_dict[d.name()] = str(val)
                    st.json(model_dict)
                else:
                    st.write("فرمول ناسازگار یا نامعین است.")
            except Exception as e:
                st.error(f"خطا: {e}")

    with col3:
        combined_input = st.text_area(
            "فرمول با سور جهانی و وجودی ترکیبی:",
            value="ForAll([x], Implies(P(x), Exists([y], Q(y))))",
            help="مثال: ForAll([x], Implies(P(x), Exists([y], Q(y))))",
            height=150
        )
        if st.button("تحلیل فرمول ترکیبی", key="combined_btn"):
            try:
                Human = DeclareSort('Human')
                x = Const('x', Human)
                y = Const('y', Human)
                P = Function('P', Human, BoolSort())
                Q = Function('Q', Human, BoolSort())

                formula = ForAll([x], Z3Implies(P(x), Exists([y], Q(y))))

                solver = Solver()
                solver.add(formula)
                result = solver.check()
                st.write(f"نتیجه حل (Combined): {result}")
                if result == sat:
                    model = solver.model()
                    model_dict = {}
                    for d in model.decls():
                        val = model[d]
                        try:
                            sort_name = val.sort().name()
                            if sort_name == 'Int':
                                model_dict[d.name()] = val.as_long()
                            else:
                                model_dict[d.name()] = str(val)
                        except AttributeError:
                            model_dict[d.name()] = str(val)
                    st.json(model_dict)
                else:
                    st.write("فرمول ناسازگار یا نامعین است.")
            except Exception as e:
                st.error(f"خطا: {e}")

elif logic_type == "حل مسئله با kanren":
    st.header("حل مسئله با kanren")

    st.markdown("کد پایتون خود را وارد کنید (کتابخانه kanren را وارد کنید و پرس‌وجوهای خود را بنویسید):")

    default_code = '''from kanren import run, var, fact, Relation, conde

# تعریف متغیرها و رابطه
parent = Relation()

# افزودن حقایق به پایگاه داده
fact(parent, "mary", "john")
fact(parent, "john", "michael")

x = var()
# پرس‌وجو: یافتن فرزندان mary
result = run(5, x, parent("mary", x))
print("فرزندان mary:", result)
'''

    code_input = st.text_area("کد کانرن خود را اینجا بنویسید:", value=default_code, height=300)

    if st.button("اجرا کردن کد"):
        import sys
        import io

        # Redirect stdout to capture print outputs
        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()

        local_vars = {}

        try:
            exec(code_input, {'__builtins__': __builtins__}, local_vars)
            output = redirected_output.getvalue()
            if output.strip():
                st.text_area("خروجی:", value=output, height=200)
            else:
                st.warning("کد اجرا شد ولی خروجی چاپی نداشت.")
        except Exception as e:
            st.error(f"خطا در اجرای کد: {e}")
        finally:
            sys.stdout = old_stdout

# Footer
st.markdown("---")
st.markdown("**پروژه پایانی کارشناسی - پیاده‌سازی مفاهیم هوش مصنوعی راسل و نوریگ**")
