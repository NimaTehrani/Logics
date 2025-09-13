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
    ["معرفی", "منطق گزاره‌ای", "منطق مرتبه اول", "حل مسئله با Z3"]
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

elif logic_type == "حل مسئله با Z3":
    st.header("حل مسئله با Z3")

    problem_type = st.selectbox(
        "نوع مسئله را انتخاب کنید:",
        ["منطق گزاره‌ای", "منطق مرتبه اول", "حساب و اعداد"]
    )

    if problem_type == "منطق گزاره‌ای":
        st.subheader("حل مسئله منطق گزاره‌ای با Z3")

        P, Q, R = Bool('P'), Bool('Q'), Bool('R')

        example_choice = st.selectbox(
            "یک مثال انتخاب کنید یا فرمول خود را وارد نمایید:",
            [
                "انتخاب مثال",
                "P و نقیض P (ناسازگار)",
                "P یا نقیض P (tautology)",
                "P سپس Q و P پس نتیجه Q",
                "فرمول دلخواه"
            ]
        )

        if example_choice == "P و نقیض P (ناسازگار)":
            expr = And(P, Not(P))
        elif example_choice == "P یا نقیض P (tautology)":
            expr = Or(P, Not(P))
        elif example_choice == "P سپس Q و P پس نتیجه Q":
            expr = And(Z3Implies(P, Q), P)
        else:
            custom_expr = st.text_input("فرمول خود را وارد کنید (با syntax Z3):", "And(P, Q)")
            try:
                expr = eval(custom_expr)
            except Exception as e:
                st.error("خطا در تفسیر فرمول")
                expr = None

        if expr is not None:
            st.write(f"**عبارت منطقی:** {expr}")

            solver = Solver()
            solver.add(expr)

            if st.button("حل مسئله"):
                result = solver.check()

                if result == sat:
                    st.success("فرمول ارضاپذیر است ✓")
                    model = solver.model()
                    st.write("**مدل یافت شده:**")
                    for decl in model:
                        st.write(f"{decl.name()} = {model[decl]}")
                else:
                    st.error("فرمول ناسازگار است ✗")

    elif problem_type == "منطق مرتبه اول":
        st.subheader("حل مسئله منطق مرتبه اول با Z3")

        Human = DeclareSort('Human')
        mortal = Function('mortal', Human, BoolSort())
        socrates = Const('socrates', Human)
        x = Const('x', Human)

        axiom1 = ForAll([x], Z3Implies(Human(x), mortal(x)))
        axiom2 = Human(socrates)

        solver = Solver()
        solver.add(axiom1, axiom2)

        conjecture = mortal(socrates)

        if st.button("بررسی استنتاج"):
            solver.push()
            solver.add(Not(conjecture))

            if solver.check() == unsat:
                st.success("✅ استنتاج معتبر است: سقراط فانی است")
            else:
                st.error("❌ استنتاج نامعتبر است")

            solver.pop()

    elif problem_type == "حساب و اعداد":
        st.subheader("حل مسائل عددی با Z3")

        x, y = Int('x'), Int('y')

        solver = Solver()
        solver.add(x + y == 10, x > y, x > 0, y > 0)

        if st.button("حل معادله x + y = 10 با x > y"):
            if solver.check() == sat:
                model = solver.model()
                st.success(f"✅ راه حل یافت شد: x = {model[x]}, y = {model[y]}")
            else:
                st.error("❌ هیچ راه حلی یافت نشد")

# Footer
st.markdown("---")
st.markdown("**پروژه پایانی کارشناسی - پیاده‌سازی مفاهیم هوش مصنوعی راسل و نوریگ**")
