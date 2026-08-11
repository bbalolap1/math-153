from __future__ import annotations

import math
import random
import re
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache

import sympy

from .complexity import (
    application_context,
    complexity_layer,
    family_complexity_evidence,
    structural_signature,
)
from .course_content import (
    COURSE_UNITS,
    PROBLEM_FAMILY_INDEX,
    SECTION_INDEX,
    ProblemFamily as CanonicalFamily,
)
from .models import (
    DifficultyLayer,
    PracticeProblem,
    ProfessorGrammar,
    WorkedSolution,
)
from .validation import validate_practice_answer


FOUNDATION = "Foundation"
CHAPTERS_12 = "Unit 1 — Chapters 1–2"
CHAPTERS_34 = "Unit 2 — Chapter 3"
CHAPTER_5 = "Unit 3 — Chapters 4–5"
MIXED_TEST = "Mixed Test Review"
FINAL_REVIEW = "Final Exam Review"


@dataclass(frozen=True)
class FamilySpec:
    family_id: str
    title: str
    group: str
    chapter: str
    section: str
    skills: tuple[str, ...]
    representations: tuple[str, ...]
    structural_variants: tuple[str, ...]
    source_refs: tuple[str, ...]


def _section_for_family(family_id: str):
    for section in SECTION_INDEX.values():
        if any(family.id == family_id for family in section.problem_families):
            return section
    raise KeyError(family_id)


def _group_for_section(section) -> str:
    if section.unit_id == "FOUNDATION":
        return FOUNDATION
    if section.unit_id == "UNIT1":
        return CHAPTERS_12
    if section.unit_id == "UNIT2":
        return CHAPTERS_34
    return CHAPTER_5


def _source_strings(family: CanonicalFamily) -> tuple[str, ...]:
    return tuple(f"{ref.document}:{ref.locator}" for ref in family.source_refs)


def _spec(family_id: str, family: CanonicalFamily) -> FamilySpec:
    section = _section_for_family(family_id)
    return FamilySpec(
        family_id=family_id,
        title=family.title,
        group=_group_for_section(section),
        chapter=str(section.chapter),
        section=section.id,
        skills=family.required_concepts,
        representations=tuple(family.representations),
        structural_variants=family.structural_variants,
        source_refs=_source_strings(family),
    )


FAMILY_SPECS: dict[str, FamilySpec] = {
    fid: _spec(fid, family) for fid, family in PROBLEM_FAMILY_INDEX.items()
}


@lru_cache
def family_source_refs() -> dict[str, list[str]]:
    return {fid: list(spec.source_refs) for fid, spec in FAMILY_SPECS.items()}


def families_for_scope(scope: str) -> list[str]:
    if scope in {MIXED_TEST, FINAL_REVIEW, "All", "Math 153"}:
        return list(FAMILY_SPECS)
    normalized = scope.casefold()
    result = [
        fid for fid, spec in FAMILY_SPECS.items()
        if spec.group.casefold() == normalized
        or spec.section.casefold() == normalized
        or f"chapter {spec.chapter}".casefold() == normalized
    ]
    if result:
        return result
    # Unit aliases and old UI labels.
    aliases = {
        "chapters 1–2": CHAPTERS_12,
        "chapters 3–4": CHAPTERS_34,
        "chapter 5": CHAPTER_5,
        "unit 1": CHAPTERS_12,
        "unit 2": CHAPTERS_34,
        "unit 3": CHAPTER_5,
    }
    target = aliases.get(normalized)
    return [fid for fid, spec in FAMILY_SPECS.items() if target and spec.group == target]


def family_variants(family_id: str, count: int = 12, seed: int = 15300) -> list[PracticeProblem]:
    return [generate_practice_problem(family_id, seed + i * 1009, i) for i in range(count)]


def _difficulty_name(layer: DifficultyLayer) -> str:
    if layer.value <= "L1":
        return "direct"
    if layer.value <= "L3":
        return "standard"
    if layer.value <= "L5":
        return "professor"
    return "mixed"


def _layer(variant: int) -> DifficultyLayer:
    # Repetition of a family should progress through cognitive demand.
    return (
        DifficultyLayer.DIRECT,
        DifficultyLayer.GUIDED,
        DifficultyLayer.REPRESENTATION,
        DifficultyLayer.MIXED,
        DifficultyLayer.PROFESSOR,
        DifficultyLayer.TIMED,
        DifficultyLayer.CUMULATIVE,
        DifficultyLayer.PROFESSOR,
    )[variant % 8]


def _sol(rule: str, setup: str, steps: list[str], answer: str, check: str, *,
         inference: str = "", prerequisite: str = "", family_reason: str = "") -> WorkedSolution:
    return WorkedSolution(
        rule=rule,
        setup=setup,
        calculation=steps,
        final_answer=answer,
        check=check,
        inference=inference or "Recognize the mathematical structure before selecting a procedure.",
        prerequisite=prerequisite or "Use the prerequisite algebra identified by the course family.",
        family_reason=family_reason or "The source-supported structure determines this family.",
    )


def _fmt_num(x) -> str:
    x = sympy.simplify(x)
    return str(x).replace("**", "^")


def _professor_grammar(family: CanonicalFamily) -> ProfessorGrammar:
    return ProfessorGrammar(
        instructional_verbs=list(family.professor_verbs),
        answer_forms=list(family.expected_answer_forms),
        hidden_requirements=list(family.verification_methods),
        surface_patterns=list(family.structural_variants),
        allowed_variations=[
            "coefficients/constants",
            "surface wording",
            "representation where source-supported",
            "context where source-supported",
            "given/unknown arrangement",
        ],
        invariants=[
            *family.required_concepts,
            *family.required_procedures,
            *family.verification_methods,
        ],
        source_examples=[f"{r.document}:{r.locator}" for r in family.source_refs],
    )


def _build_raw_base(fid: str, rng: random.Random, variant: int):
    """Return prompt, answer_type, answer, wrong, choices, solution, representation, flags."""
    k = variant % 4
    x = sympy.Symbol("x")

    # FOUNDATION / CHAPTER 1 -------------------------------------------------
    if fid == "F0-REAL-NUMBERS":
        cases = [
            (r"\sqrt{49}", "natural,whole,integer,rational,real"),
            (r"-\frac{7}{3}", "rational,real"),
            (r"\sqrt{11}", "irrational,real"),
            ("0", "whole,integer,rational,real"),
        ]
        value, ans = cases[variant % len(cases)]
        return (f"Select every real-number set that contains ${value}$.", "multi_select", ans,
                "real", ["natural","whole","integer","rational","irrational","real"],
                _sol("Use nested real-number sets.", value, [f"Classification: {ans}"], ans,
                     "Each selected set must contain the value."), "classification", {})
    if fid == "F0-ARITHMETIC":
        a,b,c = rng.randint(-10,-2), rng.randint(2,9), rng.randint(2,7)
        if k % 2:
            f1, f2 = Fraction(abs(a), b), Fraction(c, b+1)
            res = f1 - f2
            ans = str(res.numerator) if res.denominator == 1 else f"{res.numerator}/{res.denominator}"
            prompt = rf"Evaluate exactly: $\frac{{{abs(a)}}}{{{b}}}-\frac{{{c}}}{{{b+1}}}$."
            steps=[f"Use LCD {math.lcm(b,b+1)}.", f"Reduce to {ans}."]
            return (prompt,"fraction",ans,str(float(res)),[],_sol("Use exact fraction arithmetic.",prompt,steps,ans,"Check with decimals."),"symbolic",{})
        ans=a+b*(c-2)
        prompt=f"Evaluate: ${a}+{b}({c}-2)$."
        return (prompt,"integer",str(ans),str(-ans),[],_sol("Grouping before multiplication before addition.",prompt,[f"{c}-2={c-2}",f"{b}({c-2})={b*(c-2)}",f"Result={ans}"],str(ans),"Estimate sign/magnitude."),"symbolic",{})
    if fid == "CH1-REAL-ORDER":
        a,b=rng.randint(-9,9),rng.randint(2,8)
        left=Fraction(a,b); right=Fraction(a+1,b)
        ans="<" if left<right else ">"
        return (rf"Insert $<$, $>$, or $=$: $\frac{{{a}}}{{{b}}}\ \square\ \frac{{{a+1}}}{{{b}}}$.",
                "multiple_choice",ans,"=",["<",">","="],_sol("Compare real values on the number line.","same denominator",[f"{a} compared with {a+1} gives {ans}"],ans,"Same denominator confirms order."),"classification",{})
    if fid == "CH1-RADICAL-PRODUCT":
        p,q=rng.randint(2,7),rng.randint(2,6)
        # sqrt(p^2*q) -> p*sqrt(q), q squarefree-ish
        q = next(v for v in range(q, q+6) if not sympy.integer_nthroot(v,2)[1])
        prompt=rf"Simplify completely: $\sqrt{{{p*p*q}x^2}}$ for real $x$."
        ans=f"{p}*Abs(x)*sqrt({q})"
        return (prompt,"expression",ans,f"{p}*x*sqrt({q})",[],_sol(r"\sqrt{x^2}=|x|.",prompt,[rf"\sqrt{{{p*p}{q}x^2}}={p}|x|\sqrt{{{q}}}"],ans,"Square the simplified magnitude."),"symbolic",{})
    if fid == "CH1-RATIONALIZE-DENOMINATOR":
        n=rng.randint(2,10)
        q=next(v for v in range(n,n+8) if not sympy.integer_nthroot(v,2)[1])
        num=rng.randint(1,5)
        prompt=rf"Rationalize the denominator and simplify: $\frac{{{num}}}{{\sqrt{{{q}}}}}$."
        ans=f"{num}*sqrt({q})/{q}"
        return (prompt,"expression",ans,f"{num}/sqrt({q})",[],_sol("Multiply by the radical over itself.",prompt,[rf"\frac{{{num}}}{{\sqrt{{{q}}}}}\frac{{\sqrt{{{q}}}}}{{\sqrt{{{q}}}}}=\frac{{{num}\sqrt{{{q}}}}}{{{q}}}"],ans,"Denominator is rational."),"symbolic",{})
    if fid in {"CH1-FACTOR-GROUPING","CH1-FACTOR-QUADRATIC"}:
        if fid.endswith("GROUPING"):
            a,b=rng.randint(2,6),rng.randint(1,7)
            # x^3 + a x^2 + b x + ab = (x+a)(x^2+b)
            expr=sympy.expand(x**3+a*x**2+b*x+a*b)
            ans=f"(x+{a})*(x^2+{b})"
            prompt=f"Fully factor: ${sympy.sstr(expr)}$."
            steps=[f"Group: x^2(x+{a})+{b}(x+{a}).",ans]
        else:
            p,q=rng.randint(1,7),rng.randint(1,7)
            expr=sympy.expand((x-p)*(x+q)); ans=f"(x-{p})*(x+{q})"
            prompt=f"Fully factor: ${sympy.sstr(expr)}$."; steps=[ans]
        return (prompt,"expression",ans,"x",[],_sol("Factor completely and verify by multiplication.",sympy.sstr(expr),steps,ans,"Expand the factors."),"symbolic",{"requires_factoring":True})
    if fid=="CH1-RATIONALIZE-NUMERATOR":
        c=rng.randint(2,8)
        prompt=rf"Rationalize the numerator: $\frac{{\sqrt{{x+{c}}}-\sqrt{{x}}}}{{{c}}}$."
        ans=f"1/(sqrt(x+{c})+sqrt(x))"
        return (prompt,"expression",ans,"1",[],_sol("Multiply by the conjugate.",prompt,[rf"\frac{{(\sqrt{{x+{c}}}-\sqrt x)(\sqrt{{x+{c}}}+\sqrt x)}}{{{c}(\sqrt{{x+{c}}}+\sqrt x)}}",rf"\frac{{{c}}}{{{c}(\sqrt{{x+{c}}}+\sqrt x)}}"],ans,"Conjugate product removes the numerator radical difference."),"symbolic",{})
    if fid.startswith("CH1-RATIONAL-"):
        a,b=rng.sample(range(2,9),2)
        if fid=="CH1-RATIONAL-SIMPLIFY":
            prompt=rf"Simplify and state the original restriction: $\frac{{x^2-{a*a}}}{{x-{a}}}$."
            ans=f"x+{a}"
            return (prompt,"expression",ans,f"x-{a}",[],_sol("Factor first; restrictions come from the original denominator.",prompt,[f"x^2-{a*a}=(x-{a})(x+{a})",f"x+{a}, x!={a}"],ans,f"Original denominator requires x≠{a}."),"symbolic",{"requires_domain_check":True,"requires_factoring":True})
        if fid=="CH1-RATIONAL-COMBINE":
            prompt=rf"Simplify into one rational expression: $\frac{{1}}{{x-{a}}}+\frac{{1}}{{x-{b}}}$."
            ans=f"(2*x-{a+b})/((x-{a})*(x-{b}))"
            return (prompt,"expression",ans,"2*x",[],_sol("Use the LCD, then combine numerators.",prompt,[f"LCD=(x-{a})(x-{b})",f"Numerator=(x-{b})+(x-{a})=2x-{a+b}"],ans,f"x≠{a},{b}."),"symbolic",{"requires_domain_check":True,"requires_factoring":True})
        if fid=="CH1-RATIONAL-DIVIDE":
            prompt=rf"Simplify: $\frac{{x^2-{a*a}}}{{x-{b}}}\div\frac{{x-{a}}}{{x+{b}}}$."
            ans=f"(x+{a})*(x+{b})/(x-{b})"
            return (prompt,"expression",ans,"x",[],_sol("Multiply by the reciprocal, factor, then cancel factors.",prompt,[f"x^2-{a*a}=(x-{a})(x+{a})","Invert the divisor.",ans],ans,"Preserve restrictions from both original denominators and the divisor."),"symbolic",{"requires_domain_check":True,"requires_factoring":True})

    # CHAPTER 2 -------------------------------------------------------------
    if fid=="CH2-EQUATION-CLASSIFY":
        a=rng.randint(2,8)
        typ=variant%3
        if typ==0:
            prompt=f"Classify and give the solution set: ${a}(x+1)={a}x+{a}$."; ans="all real numbers"
        elif typ==1:
            prompt=f"Classify and give the solution set: ${a}(x+1)={a}x+{a+1}$."; ans="no solution"
        else:
            sol=rng.randint(-5,6); b=rng.randint(-6,6); c=a*sol+b
            prompt=f"Solve and classify: ${a}x+{b}={c}$."; ans=str(sol)
        return (prompt,"multiple_choice",ans,"no solution",["all real numbers","no solution",ans],_sol("Simplify both sides and inspect the remaining statement.",prompt,[f"Result: {ans}"],ans,"Check the resulting statement/candidate."),"classification",{})
    if fid=="CH2-RATIONAL-EQUATIONS":
        a,b=rng.sample(range(1,7),2); sol=a+b
        # 1/(x-a)+1/(x-b) constructed with x= a+b? not guaranteed. Build simple 1/(x-a)=1/b => x=a+b
        prompt=rf"State the domain, then solve: $\frac{{1}}{{x-{a}}}=\frac{{1}}{{{b}}}$."
        ans=str(sol)
        return (prompt,"solution_set",ans,str(a),[],_sol("Record denominator restrictions before clearing denominators.",prompt,[f"x≠{a}",f"{b}=x-{a}",f"x={sol}"],ans,f"{sol} is allowed and satisfies the original equation."),"symbolic",{"requires_domain_check":True})
    if fid=="CH2-MIXTURE":
        q=rng.randint(20,60); p1,p2,target=0.2,0.5,0.35
        # x of p2 in q total target: .5x+.2(q-x)=.35q => .3x=.15q => x=q/2
        if q%2: q+=1
        ans=str(q//2)
        prompt=f"A {q}-liter mixture must be 35% concentrate using 20% and 50% solutions. How many liters of the 50% solution are needed?"
        return (prompt,"decimal",f"{q/2:.1f}",f"{q:.1f}",[],_sol("Conserve amount of concentrate.",prompt,[f"0.50x+0.20({q}-x)=0.35({q})",f"x={q/2:.1f}"],f"{q/2:.1f}","Mixture amounts total correctly."),"context",{"requires_interpretation":True,"requires_multiple_methods":True})
    if fid=="CH2-RATE-MOTION-WORK":
        if k<2:
            r1,r2=rng.randint(40,65),rng.randint(25,45); t=rng.randint(2,5)
            d=(r1+r2)*t
            prompt=f"Two vehicles leave the same point in opposite directions at {r1} mph and {r2} mph. How many hours until they are {d} miles apart?"
            ans=str(t)
            steps=[f"Combined separation rate={r1+r2} mph.",f"t={d}/{r1+r2}={t}."]
        else:
            a,b=rng.randint(3,8),rng.randint(3,8)
            # combined time ab/(a+b)
            res=Fraction(a*b,a+b); ans=f"{res.numerator}/{res.denominator}"
            prompt=f"One worker finishes a job in {a} hours and another in {b} hours. Working together, how many hours are required?"
            steps=[f"Combined rate=1/{a}+1/{b}={(a+b)}/{a*b}.",f"Time={ans} hours."]
        return (prompt,"fraction" if "/" in ans else "integer",ans,"0",[],_sol("Model rates, not times, then solve.",prompt,steps,ans,"Substitute into the rate relationship."),"context",{"requires_interpretation":True,"requires_multiple_methods":True})
    if fid=="CH2-FORMULA-REARRANGE":
        prompt=r"Solve the formula $A=P(1+rt)$ for $r$."
        ans="(A/P-1)/t"
        return (prompt,"expression",ans,"A/P",[],_sol("Use inverse operations symbolically.",prompt,["A/P=1+rt","A/P-1=rt","r=(A/P-1)/t"],ans,"Substitute the result back into the formula."),"symbolic",{"requires_multiple_methods":True})
    if fid in {"CH2-QUADRATIC-METHOD-SELECTION","CH2-COMPLETING-SQUARE","CH2-QUADRATIC-TYPE"}:
        if fid=="CH2-COMPLETING-SQUARE":
            a=rng.randint(1,4); h=rng.randint(-5,5); c=rng.randint(-6,8)
            expr=sympy.expand(a*(x-h)**2+c)
            ans=f"{a}*(x-{h})^2+({c})"
            prompt=f"Write in completed-square form: ${sympy.sstr(expr)}$."
            return (prompt,"expression",ans,str(expr),[],_sol("Normalize, take half the x coefficient, and compensate the constant.",sympy.sstr(expr),[ans],ans,"Expand to recover the original polynomial."),"symbolic",{"requires_multiple_methods":True})
        if fid=="CH2-QUADRATIC-TYPE":
            p,q=rng.randint(1,5),rng.randint(1,5)
            # x^4 -(p+q)x^2+pq=0 -> x^2=p or q
            expr=x**4-(p+q)*x**2+p*q
            roots=set()
            for v in {p,q}:
                s=int(math.isqrt(v))
                if s*s==v:
                    roots|={-s,s}
            if not roots:
                p,q=1,4; expr=x**4-5*x**2+4; roots={-2,-1,1,2}
            ans=",".join(str(v) for v in sorted(roots))
            prompt=f"Find all real solutions: ${sympy.sstr(expr)}=0$."
            return (prompt,"solution_set",ans,"1,4",[],_sol("Use u=x^2 to expose a quadratic.",prompt,["Let u=x^2.","Solve the quadratic in u.","Back-substitute and keep real x."],ans,"Substitute each real candidate."),"symbolic",{"requires_multiple_methods":True,"requires_factoring":True})
        # method selection
        p,q=rng.randint(1,6),rng.randint(1,6)
        expr=sympy.expand((x-p)*(x-q)); ans=",".join(map(str,sorted({p,q})))
        wording=["Solve", "Find all real numbers satisfying", "Determine the zeros of", "Without graphing, solve"][k]
        prompt=f"{wording}: ${sympy.sstr(expr)}=0$."
        return (prompt,"solution_set",ans,str(p+q),[],_sol("Select a valid quadratic method; factoring is efficient here.",prompt,[f"(x-{p})(x-{q})=0",f"x={p} or x={q}"],ans,"Substitute roots."),"symbolic",{"requires_factoring":True})
    if fid=="CH2-COMPLEX-QUOTIENT":
        a,b,c,d=[rng.randint(1,7) for _ in range(4)]
        z=sympy.simplify((a+b*sympy.I)/(c+d*sympy.I))
        ans=str(sympy.expand_complex(z)).replace("I","i")
        prompt=rf"Simplify into $a+bi$: $\frac{{{a}+{b}i}}{{{c}+{d}i}}$."
        return (prompt,"complex_number",ans,"0",[],_sol("Multiply by the denominator's conjugate.",prompt,[f"Use {c}-{d}i.",f"Result={ans}"],ans,"Denominator becomes real."),"symbolic",{})
    if fid=="CH2-COMPLEX-COMPONENT-EQUATIONS":
        xv,yv=rng.randint(-4,5),rng.randint(-5,5)
        # (2x+3)+(y-1)i = known
        real=2*xv+3; imag=yv-1
        prompt=rf"Find real $x,y$ satisfying $(2x+3)+(y-1)i={real}+{imag}i$."
        ans=f"{xv},{yv}"
        return (prompt,"solution_set",ans,f"{real},{imag}",[],_sol("Equal complex numbers have equal real and imaginary parts.",prompt,[f"2x+3={real} -> x={xv}",f"y-1={imag} -> y={yv}"],ans,"Both components match."),"symbolic",{})
    if fid=="CH2-ABS-EQUATIONS":
        h=rng.randint(-5,5); d=rng.randint(1,8)
        ans=f"{h-d},{h+d}"
        prompt=rf"Find all real solutions: $|x-({h})|={d}$."
        return (prompt,"solution_set",ans,str(h),[],_sol("Distance d from h gives two cases.",prompt,[f"x-{h}={d} or x-{h}=-{d}",f"x={h+d} or x={h-d}"],ans,"Both values give absolute value d."),"symbolic",{})
    if fid=="CH2-RADICAL-EQUATIONS":
        sol=rng.randint(1,9); c=rng.randint(1,6); rhs=sol+c
        # sqrt(x)=? choose x=sol^2
        target=sol
        prompt=rf"Solve and check in the original equation: $\sqrt{{x+{c}}}={target}$."
        ans=str(target*target-c)
        return (prompt,"solution_set",ans,str(target*target),[],_sol("Isolate the radical, square, then check.",prompt,[f"x+{c}={target*target}",f"x={ans}"],ans,"Original radical evaluates to the nonnegative target."),"symbolic",{"requires_extraneous_check":True})
    if fid=="CH2-COMPOUND-INEQUALITY":
        a,b=sorted(rng.sample(range(-8,9),2))
        prompt=f"Solve and write in interval notation: ${a}<2x+1\\le {2*b+1}$."
        left=Fraction(a-1,2); ans=f"({left},{b}]"
        return (prompt,"interval",ans,"",[],_sol("Apply the same operations to all three parts.",prompt,[f"{a-1}<2x≤{2*b}",f"{left}<x≤{b}"],ans,"Check endpoints and strictness."),"symbolic",{})
    if fid=="CH2-ABS-INEQUALITY":
        h=rng.randint(-4,4); d=rng.randint(2,7)
        prompt=rf"Solve: $|x-({h})|>{d}$. Write the answer in interval notation."
        ans=f"(-oo,{h-d}) U ({h+d},oo)"
        return (prompt,"interval",ans,"",[],_sol("Greater-than absolute value means outside the central interval.",prompt,[f"x<{h-d} or x>{h+d}"],ans,"Endpoints are excluded for >."),"symbolic",{})
    if fid in {"CH2-POLYNOMIAL-INEQUALITY","CH2-RATIONAL-INEQUALITY"}:
        a,b=sorted(rng.sample(range(-5,7),2))
        if fid=="CH2-POLYNOMIAL-INEQUALITY":
            prompt=rf"Find all real numbers satisfying $(x-({a}))(x-({b}))\le0$."
            ans=f"[{a},{b}]"; flags={"requires_factoring":True}
        else:
            prompt=rf"Solve and write in interval notation: $\frac{{x-({a})}}{{x-({b})}}>0$."
            # sign positive (-inf,a) U (b,inf) if a<b
            ans=f"(-oo,{a}) U ({b},oo)"; flags={"requires_domain_check":True,"requires_factoring":True}
        return (prompt,"interval",ans,"",[],_sol("Use critical points and a sign chart.",prompt,[f"Critical values: {a}, {b}.",f"Selected intervals: {ans}"],ans,"Test one point per interval; respect excluded denominator values."),"symbolic",flags)

    # CHAPTER 3 -------------------------------------------------------------
    if fid=="CH3-DISTANCE-MIDPOINT":
        x1,y1=rng.randint(-5,4),rng.randint(-5,4); dx,dy=3,4; x2,y2=x1+dx,y1+dy
        if k%2==0:
            prompt=f"Find the distance between $({x1},{y1})$ and $({x2},{y2})$."; ans="5"; at="integer"
            steps=[r"d=\sqrt{3^2+4^2}=5"]
        else:
            prompt=f"Find the midpoint of the segment joining $({x1},{y1})$ and $({x2},{y2})$."; ans=f"{Fraction(x1+x2,2)},{Fraction(y1+y2,2)}"; at="ordered_pair"
            steps=[f"M=(({x1}+{x2})/2,({y1}+{y2})/2)={ans}"]
        return (prompt,at,ans,"",[],_sol("Use the requested coordinate formula.",prompt,steps,ans,"Verify against the endpoints."),"symbolic",{})
    if fid=="CH3-PERP-BISECTOR":
        # Segment horizontal: A(-a,0), B(a,0), point P(0,p) always equal distance and perpendicular bisector x=0
        a,p=rng.randint(2,6),rng.randint(1,7)
        prompt=f"Determine, with working, whether $P=(0,{p})$ lies on the perpendicular bisector of the segment from $A=(-{a},0)$ to $B=({a},0)$."
        ans="yes"
        return (prompt,"multiple_choice",ans,"no",["yes","no"],_sol("A point is on a perpendicular bisector iff it is equidistant from the endpoints.",prompt,[f"PA^2={a*a+p*p}",f"PB^2={a*a+p*p}","Therefore PA=PB."],ans,"Equal distances verify membership."),"verbal",{"requires_interpretation":True})
    if fid=="CH3-CIRCLE-CENTER-RADIUS":
        h,k0,r=rng.randint(-4,4),rng.randint(-4,4),rng.randint(2,7)
        if variant%2==0:
            prompt=f"Write the equation of the circle with center $({h},{k0})$ and radius ${r}$."
            ans=f"(x-({h}))^2+(y-({k0}))^2={r*r}"
            at="equation"; steps=[ans]
        else:
            # Ask center as ordered pair from standard equation
            prompt=rf"Find the center of $(x-({h}))^2+(y-({k0}))^2={r*r}$."
            ans=f"{h},{k0}"; at="ordered_pair"; steps=[f"Center=({h},{k0})"]
        return (prompt,at,ans,"",[],_sol(r"(x-h)^2+(y-k)^2=r^2.",prompt,steps,ans,"Read signs carefully."),"symbolic",{})
    if fid=="CH3-CIRCLE-INTERCEPTS":
        r=rng.randint(2,7)
        if k==0:
            prompt=rf"Find all x-intercepts of $x^2+y^2={r*r}$."
            ans=f"(-{r},0);({r},0)"
        elif k==1:
            prompt=rf"Find all y-intercepts of $(x-1)^2+y^2={r*r}$."
            val=sympy.sqrt(r*r-1)
            ans=f"(0,-sqrt({r*r-1}));(0,sqrt({r*r-1}))"
        elif k==2:
            prompt=rf"Find all x-intercepts of $(x-{r})^2+y^2=0$."
            ans=f"({r},0)"
            return (prompt,"ordered_pair",ans,"",[],_sol("Set y=0 and solve the resulting square equation.",prompt,[f"(x-{r})^2=0",f"x={r}"],ans,"The circle of radius 0 meets the axis once."),"symbolic",{})
        else:
            prompt=rf"Does the circle $(x)^2+(y-{r+2})^2={r*r}$ have any x-intercepts?"
            ans="no"
            return (prompt,"multiple_choice",ans,"yes",["yes","no"],_sol("Set y=0 and check whether the resulting x^2 value is nonnegative.",prompt,[f"x^2+{(r+2)**2}={r*r}",f"x^2={r*r-(r+2)**2}<0"],ans,"No real x satisfies the intercept equation."),"verbal",{"requires_interpretation":True})
        return (prompt,"ordered_pairs",ans,"",[],_sol("Set the other coordinate to zero and solve.",prompt,["Substitute the axis condition.","Solve the resulting quadratic/root equation."],ans,"Substitute every intercept into the circle equation."),"symbolic",{})
    if fid=="CH3-GRAPH-SYMMETRY":
        cases=[("x^2+y^2=25","x-axis,y-axis,origin"),("y=x^2","y-axis"),("y=x^3","origin")]
        eq,ans=cases[variant%len(cases)]
        choices=["x-axis","y-axis","origin","x-axis,y-axis,origin","none"]
        return (f"Determine every symmetry of ${eq}$.", "multiple_choice", ans, "none", choices,
                _sol("Test x→-x, y→-y, and both substitutions.",eq,[f"Symmetry: {ans}"],ans,"Substitution leaves the equation unchanged exactly for the reported symmetries."),"classification",{})
    if fid=="CH3-LINE-EQUATION":
        x1,y1=rng.randint(-4,4),rng.randint(-5,5); m=rng.choice([-3,-2,-1,1,2,3])
        b=y1-m*x1
        if k==0:
            prompt=f"Find the slope-intercept form of the line through $({x1},{y1})$ with slope ${m}$."
        elif k==1:
            prompt=f"Find the line through $({x1},{y1})$ parallel to $y={m}x+7$."
        elif k==2:
            base=Fraction(-1,m); prompt=f"Find the line through $({x1},{y1})$ perpendicular to a line of slope ${base}$."
        else:
            prompt=f"A linear model has rate of change ${m}$ and passes through $({x1},{y1})$. Write its equation."
        ans=f"y={m}*x+({b})"
        return (prompt,"equation",ans,"",[],_sol("Use y-y1=m(x-x1), then convert if requested.",prompt,[f"y-{y1}={m}(x-{x1})",ans],ans,f"Point ({x1},{y1}) satisfies the equation."),"context" if k==3 else "symbolic",{"requires_interpretation":k>0})
    if fid=="CH3-DOMAIN-FORMULA":
        a,b=sorted(rng.sample(range(1,8),2))
        if k==0:
            prompt=rf"Find the domain of $f(x)=\sqrt{{x-{a}}}$ and write it in interval notation."
            ans=f"[{a},oo)"
            steps=[f"x-{a}≥0",f"x≥{a}"]
        elif k==1:
            prompt=rf"Find the domain of $f(x)=\frac{{x+1}}{{x-{b}}}$."
            ans=f"(-oo,{b}) U ({b},oo)"
            steps=[f"x-{b}≠0",f"x≠{b}"]
        elif k==2:
            prompt=rf"Find the domain of $f(x)=\frac{{\sqrt{{x-{a}}}}}{{x-{b}}}$ and write it in interval notation."
            ans=f"[{a},{b}) U ({b},oo)"
            steps=[f"x≥{a}",f"x≠{b}",f"Intersect the restrictions: {ans}"]
        else:
            prompt=rf"Before simplifying, find the domain of $f(x)=\frac{{(x-{b})(x+2)}}{{x-{b}}}$."
            ans=f"(-oo,{b}) U ({b},oo)"
            steps=[f"Original denominator requires x≠{b}.","Cancellation does not restore the excluded input."]
        return (prompt,"domain",ans,"",[],_sol("Combine all restrictions from the original function.",prompt,steps,ans,"Every allowed input makes the original formula defined."),"symbolic",{"requires_domain_check":True})
    if fid=="CH3-GRAPH-DOMAIN-RANGE-BEHAVIOR":
        if k==0:
            prompt="A graph has one piece on [-4,-1) and another on (2,5]. State its domain."
            ans="[-4,-1) U (2,5]"; at="domain"; choices=[]
            sol_steps=["Read horizontal coverage of each piece.","Respect open/closed endpoints."]
        elif k==1:
            prompt="A disconnected graph covers x-values (-oo,-2] and [1,4). Which interval notation gives its domain?"
            ans="(-oo,-2] U [1,4)"; at="multiple_choice"
            choices=[ans,"(-oo,4)","[-2,1]","(-2,1)"]
            sol_steps=["Take the union of the two horizontal pieces."]
        elif k==2:
            prompt="From a graph, one piece has range [-3,2] and another has range [1,5). State the total range."
            ans="[-3,5)"; at="range"; choices=[]
            sol_steps=["Combine overlapping vertical coverage.","The overlap [1,2] makes the total one interval."]
        else:
            prompt="A function is constant on [-3,-1], decreases on [-1,2], then increases on [2,5]. On which interval is it constant?"
            ans="[-3,-1]"; at="multiple_choice"
            choices=[ans,"[-1,2]","[2,5]","[-3,5]"]
            sol_steps=["Constant means the output does not change as x changes."]
        return (prompt,at,ans,"",choices,_sol("Read the requested graph feature from horizontal/vertical behavior.",prompt,sol_steps,ans,"Endpoint type and direction match the stated graph."),"graph",{"requires_interpretation":True,"requires_graph":True})
    if fid=="CH3-DIFFERENCE-QUOTIENT":
        if k==0:
            a,b,c=rng.randint(1,4),rng.randint(-5,5),rng.randint(-4,4)
            f=a*x**2+b*x+c
            ans=f"{2*a}*x+{a}*h+({b})"
            prompt=rf"For $f(x)={sympy.sstr(f)}$, simplify $\frac{{f(x+h)-f(x)}}{{h}}$, $h\ne0$."
            steps=[f"f(x+h)={a}(x+h)^2+({b})(x+h)+({c})","Expand and subtract f(x).",f"Factor h and divide: {ans}"]
        elif k==1:
            a=rng.randint(1,5)
            prompt=rf"For $f(x)=\frac1{{x+{a}}}$, simplify $\frac{{f(x+h)-f(x)}}h$."
            ans=f"-1/((x+h+{a})*(x+{a}))"
            steps=["Combine the two rational terms over a common denominator.","The numerator becomes -h.","Cancel h with h≠0."]
        elif k==2:
            a=rng.randint(1,6)
            prompt=rf"For $f(x)=\sqrt{{x+{a}}}$, rationalize as needed and simplify $\frac{{f(x+h)-f(x)}}h$."
            ans=f"1/(sqrt(x+h+{a})+sqrt(x+{a}))"
            steps=["Multiply numerator and denominator by the conjugate.","The numerator becomes h.","Cancel h."]
        else:
            a,b=rng.randint(1,5),rng.randint(-4,4)
            prompt=rf"If $f(t)={a}t+({b})$, find and simplify $\frac{{f(t+k)-f(t)}}k$ for $k\ne0$."
            ans=str(a)
            steps=[f"f(t+k)={a}(t+k)+({b})","Subtract f(t).",f"Divide {a}k by k."]
        return (prompt,"expression",ans,"",[],_sol("Substitute the shifted input everywhere, subtract, then simplify legally.",prompt,steps,ans,"The quotient matches the secant-rate structure and respects the nonzero increment."),"symbolic",{"requires_multiple_methods":k in {1,2}})
    if fid=="CH3-FUNCTION-COMPOSITION":
        a,b,c=rng.randint(2,5),rng.randint(-4,4),rng.randint(1,5)
        val=rng.randint(-3,3)
        if k==0:
            ans=str(a*(val*val+c)+b)
            prompt=f"Let f(x)={a}x+({b}) and g(x)=x^2+{c}. Find (f∘g)({val})."
            steps=[f"g({val})={val*val+c}",f"f({val*val+c})={ans}"]; at="integer"; rep="symbolic"
        elif k==1:
            # symbolic reverse order
            ans=f"({a}*x+({b}))^2+{c}"
            prompt=f"For f(x)={a}x+({b}) and g(x)=x^2+{c}, find (g∘f)(x)."
            steps=["The inner function is f.",f"g(f(x))=({a}x+({b}))^2+{c}"]; at="expression"; rep="symbolic"
        elif k==2:
            # source-style table composition
            prompt="A table gives g(2)=5 and a second table gives f(5)=-3. Find (f∘g)(2)."
            ans="-3"; steps=["g(2)=5.","Use that output as the input of f: f(5)=-3."]; at="integer"; rep="table"
        else:
            prompt="A sensor converts temperature T to voltage g(T), and a display converts voltage v to a reading f(v). Which composition gives the display reading directly from temperature?"
            ans="f(g(T))"; steps=["Temperature enters g first.","The output of g becomes the input of f."]; at="multiple_choice"; rep="context"
            return (prompt,at,ans,"g(f(T))",["f(g(T))","g(f(T))","f(T)+g(T)","f(T)g(T)"],_sol("Composition follows the order of the real process.",prompt,steps,ans,"The output of the inner process is a valid input to the outer process."),rep,{"requires_interpretation":True})
        return (prompt,at,ans,"",[],_sol("Evaluate/construct the inner function first, then the outer.",prompt,steps,ans,"Composition order matches the notation."),rep,{"requires_multiple_methods":True})
    if fid=="CH3-FUNCTION-QUOTIENT-DOMAIN":
        a=rng.randint(2,6)
        if k in {0,2}:
            prompt=rf"Let $f(x)=x^2-{a*a}$ and $g(x)=x-{a}$. Simplify $(f/g)(x)$ and state the original domain restriction."
            ans=f"x+{a}"
            steps=[f"(x-{a})(x+{a})/(x-{a})",f"x+{a}, x≠{a}"]
        else:
            b=a+2
            prompt=rf"Let $f(x)=\sqrt{{x-{a}}}$ and $g(x)=x-{b}$. State the domain of $(f/g)(x)$."
            ans=f"[{a},{b}) U ({b},oo)"
            return (prompt,"domain",ans,"",[],_sol("Intersect both function domains and exclude zeros of the quotient denominator.",prompt,[f"x≥{a}",f"x≠{b}",f"Domain={ans}"],ans,"Every allowed x makes f real and g nonzero."),"symbolic",{"requires_domain_check":True,"requires_multiple_methods":True})
        return (prompt,"expression",ans,"",[],_sol("The quotient inherits g(x)≠0 even after cancellation.",prompt,steps,ans,f"x={a} remains excluded."),"symbolic",{"requires_domain_check":True,"requires_factoring":True})
    # CHAPTER 4 -------------------------------------------------------------
    if fid=="CH4-POLYNOMIAL-DIVISION":
        a,b=rng.randint(1,5),rng.randint(-4,4)
        divisor=x-a; quotient=x**2+b*x+1; rem=rng.randint(-3,3)
        dividend=sympy.expand(divisor*quotient+rem)
        ans=f"{sympy.sstr(quotient)};{rem}"
        prompt=f"Divide ${sympy.sstr(dividend)}$ by $x-{a}$. Give the quotient and remainder."
        # text form easier to accept exact pair via custom validation later
        return (prompt,"text",ans,"",[],_sol("Use polynomial division; remainder degree is below divisor degree.",prompt,[f"Quotient={sympy.sstr(quotient)}",f"Remainder={rem}"],ans,f"(x-{a})({sympy.sstr(quotient)})+{rem}={sympy.sstr(dividend)}."),"symbolic",{"requires_multiple_methods":True})
    if fid=="CH4-REMAINDER-FACTOR":
        a=rng.randint(-4,5)
        # f=(x-a)*(x^2+2)+r
        rem=rng.randint(-5,5)
        poly=sympy.expand((x-a)*(x**2+2)+rem)
        prompt=f"Without long division, find the remainder when ${sympy.sstr(poly)}$ is divided by $x-({a})$."
        ans=str(rem)
        return (prompt,"integer",ans,str(a),[],_sol("Remainder theorem: remainder=f(a).",prompt,[f"f({a})={rem}"],ans,"Direct substitution gives the remainder."),"symbolic",{"requires_interpretation":True})
    if fid=="CH4-BUILD-POLYNOMIAL":
        roots=rng.sample(range(-4,5),3)
        ans="*".join(f"(x-({r}))" for r in roots)
        prompt=f"Find a monic cubic polynomial with zeros {', '.join(map(str,roots))}. Give it in factored form."
        return (prompt,"expression",ans,"",[],_sol("Each zero r gives factor x-r.",prompt,[ans],ans,"Substituting each listed zero gives 0."),"symbolic",{"requires_factoring":True})
    if fid=="CH4-POLY-SIGN-GRAPH":
        a,b=sorted(rng.sample(range(-4,6),2))
        prompt=rf"For $f(x)=(x-({a}))(x-({b}))$, find where $f(x)<0$."
        ans=f"({a},{b})"
        return (prompt,"interval",ans,"",[],_sol("Use zeros as sign-chart critical values.",prompt,[f"Zeros {a},{b}.","A positive-leading quadratic is negative between simple roots."],ans,"Test a point between the roots."),"symbolic",{"requires_graph":True,"requires_factoring":True,"requires_interpretation":True})
    if fid=="CH4-IVT":
        # f=x^3-x-1; values at 1=-1,2=5
        prompt=r"Use the Intermediate Value Theorem to decide whether $f(x)=x^3-x-1$ has a real zero in $(1,2)$."
        ans="yes"
        return (prompt,"multiple_choice",ans,"no",["yes","no"],_sol("A polynomial is continuous; opposite endpoint signs force a zero between.",prompt,["f(1)=-1","f(2)=5","0 lies between -1 and 5."],ans,"IVT guarantees existence, not the exact root."),"verbal",{"requires_interpretation":True})

    # CHAPTER 5 -------------------------------------------------------------
    if fid=="CH5-INVERSE-ALGEBRA":
        a=rng.choice([2,3,4,5]); b=rng.randint(-6,6)
        prompt=f"Find the inverse of $f(x)={a}x+({b})$."
        ans=f"(x-({b}))/{a}"
        return (prompt,"expression",ans,"",[],_sol("Swap x,y and solve for y.",prompt,[f"x={a}y+({b})",f"y=(x-({b}))/{a}"],ans,"Compose f(f^-1(x))=x."),"symbolic",{"requires_multiple_methods":True})
    if fid=="CH5-INVERSE-DOMAIN-RANGE":
        # Möbius f=(2x-7)/(3x+1): domain x!=-1/3, range y!=2/3
        prompt=r"For $f(x)=\frac{2x-7}{3x+1}$, state the range using inverse-function reasoning."
        ans="(-oo,2/3) U (2/3,oo)"
        return (prompt,"range",ans,"",[],_sol("The range of f is the domain of f^-1.",prompt,["Solve y=(2x-7)/(3x+1) for x.","The inverse denominator is 3y-2, so y≠2/3."],ans,"No x produces y=2/3."),"symbolic",{"requires_domain_check":True,"requires_multiple_methods":True})
    if fid=="CH5-EQUAL-BASE":
        base=rng.choice([2,3,5]); sol=rng.randint(-4,6); a=rng.randint(2,5); b=a*sol-rng.randint(-4,4)
        # easier construct exponent ax+c = bx+d; just base^(2x+1)=base^(sol?); 
        c=rng.randint(-5,5); d=a*sol+c
        prompt=rf"Find all real solutions: ${base}^{{{a}x+({c})}}={base}^{{{d}}}$."
        ans=str(sol)
        return (prompt,"solution_set",ans,"",[],_sol("Equal valid bases imply equal exponents.",prompt,[f"{a}x+({c})={d}",f"x={sol}"],ans,"Substitute into exponents."),"symbolic",{})
    if fid=="CH5-EXP-MODEL":
        a=rng.randint(20,80); b=rng.choice([1.05,1.1,1.2]); t=rng.randint(3,6)
        val=a*(b**t)
        prompt=f"A quantity is {a} at t=0 and follows $A(t)={a}({b})^t$. Find A({t}) to two decimals."
        ans=f"{val:.2f}"
        return (prompt,"decimal",ans,"",[],_sol("Evaluate the exponential model at the requested time.",prompt,[f"A({t})={a}({b})^{t}={ans}"],ans,"Growth factor is applied t times."),"context",{"requires_interpretation":True})
    if fid=="CH5-EXP-FROM-FEATURES":
        a=rng.randint(2,6); c=rng.randint(-4,4)
        # f=a*2^x+c has y-int a+c and asymptote c
        prompt=f"An exponential function has form $f(x)=a2^x+c$, horizontal asymptote $y={c}$, and y-intercept $(0,{a+c})$. Find a."
        ans=str(a)
        return (prompt,"integer",ans,"",[],_sol("At x=0, 2^0=1, so f(0)=a+c.",prompt,[f"a+{c}={a+c}",f"a={a}"],ans,"Matches the given intercept and asymptote."),"verbal",{"requires_interpretation":True})
    if fid=="CH5-CONTINUOUS-COMPOUND":
        P=rng.choice([1000,2500,5000]); r=rng.choice([0.03,0.04,0.05]); t=rng.randint(2,6)
        A=P*math.exp(r*t); ans=f"{A:.2f}"
        prompt=f"Find the amount after {t} years if ${P} is invested at {100*r:.0f}% compounded continuously. Round to cents."
        return (prompt,"decimal",ans,"",[],_sol(r"A=Pe^{rt}.",prompt,[f"A={P}e^({r}·{t})={ans}"],ans,"Amount exceeds principal for positive r,t."),"context",{"requires_interpretation":True})
    if fid=="CH5-LOG-CONVERT":
        base=rng.choice([2,3,5]); exp=rng.randint(2,5); value=base**exp
        if k%2==0:
            prompt=rf"Write $\log_{{{base}}}({value})={exp}$ in exponential form."
            ans=f"{base}^{exp}={value}"; at="equation"
        else:
            prompt=rf"Write ${base}^{exp}={value}$ in logarithmic form."
            ans=f"log({value})/log({base})={exp}"; at="equation" # equivalent equation not ideal parser
        return (prompt,at,ans,"",[],_sol(r"\log_b(x)=y iff b^y=x.",prompt,[ans],ans,"Both forms state the same base/exponent relationship."),"symbolic",{})
    if fid=="CH5-LOG-EQUAL":
        sol=rng.randint(3,9); a=rng.randint(1,sol-1)
        prompt=rf"Find all real solutions and check the original domain: $\ln(x-{a})=\ln({sol-a})$."
        ans=str(sol)
        return (prompt,"solution_set",ans,"",[],_sol("ln is one-to-one on positive arguments.",prompt,[f"x-{a}={sol-a}",f"x={sol}",f"x-{a}>0 is satisfied."],ans,"Original log argument is positive."),"symbolic",{"requires_domain_check":True})
    if fid=="CH5-LOG-GRAPH":
        base=rng.choice([2,3,5])
        prompt=rf"The graph of $y={base}^x$ has horizontal asymptote $y=0$. What is the corresponding asymptote of its inverse $y=\log_{{{base}}}x$?"
        ans="x=0"
        return (prompt,"multiple_choice",ans,"y=0",["x=0","y=0","x=1","y=1"],_sol("Inverse graphs reflect across y=x, swapping horizontal and vertical features.",prompt,["y=0 reflects to x=0."],ans,"The logarithm domain is x>0."),"verbal",{"requires_interpretation":True})
    if fid=="CH5-LOG-EXPAND-CONDENSE":
        if k%2==0:
            prompt=r"Expand completely: $\ln\left(\frac{x^3\sqrt{y}}{z^2}\right)$."
            ans="3*log(x)+1/2*log(y)-2*log(z)"
        else:
            prompt=r"Condense to one logarithm: $2\ln x+\ln y-\ln z$."
            ans="log(x^2*y/z)"
        return (prompt,"logarithmic_expression",ans,"",[],_sol("Use product, quotient, and power rules.",prompt,[ans],ans,"Reversing the log rules recovers the original form."),"symbolic",{})
    if fid=="CH5-LOG-PROPERTY-EQUATION":
        # ln x + ln(x-1)=ln 6 -> x(x-1)=6 -> x=3,-2 domain x>1 =>3
        prompt=r"Solve and check the original domain: $\ln x+\ln(x-1)=\ln 6$."
        ans="3"
        return (prompt,"solution_set",ans,"-2",[],_sol("Condense logs, use one-to-one behavior, then enforce positivity.",prompt,[r"\ln(x(x-1))=\ln6",r"x^2-x-6=0",r"x=3,-2",r"Domain x>1 leaves x=3."],ans,"Both original log arguments are positive at x=3."),"symbolic",{"requires_domain_check":True,"requires_factoring":True,"requires_multiple_methods":True})
    if fid=="CH5-EXP-LOG-SOLVE":
        base=rng.choice([2,3,5]); N=rng.randint(7,40)
        prompt=rf"Solve ${{{base}}}^x={N}$. Give an exact logarithmic form."
        ans=f"log({N})/log({base})"
        return (prompt,"logarithmic_expression",ans,"",[],_sol("Take logs and use the power rule.",prompt,[f"x log({base})=log({N})",ans],ans,"Raising the base to the result returns N."),"symbolic",{"requires_multiple_methods":True})
    if fid=="CH5-EXP-MIXED-SUBSTITUTION":
        base=rng.choice([2,3,5])
        # u + 1/u = 5/2 -> 2u^2-5u+2=0 u=2 or 1/2 -> x= +/- log_base 2 (if base 2 then ±1)
        if base==2:
            ans="-1,1"
        else:
            ans=f"-log(2)/log({base}),log(2)/log({base})"
        prompt=rf"Solve for real $x$: ${base}^x+{base}^{{-x}}=\frac52$."
        return (prompt,"solution_set",ans,"",[],_sol(f"Let u={base}^x>0 and rewrite {base}^(-x)=1/u.",prompt,[r"u+1/u=5/2",r"2u^2-5u+2=0",r"u=2 or 1/2","Back-substitute."],ans,"Both positive u-values are valid."),"symbolic",{"requires_multiple_methods":True})
    raise KeyError(f"No generator implemented for canonical family {fid}")



def _build_raw(fid: str, rng: random.Random, variant: int):
    """Canonical generator with source-supported structural branches before base fallback."""
    k = variant % 4
    x = sympy.Symbol("x")

    if fid == "CH1-REAL-ORDER":
        if k == 0:
            a,b=rng.randint(1,9),rng.randint(2,9); dec=round(a/b + 0.1, 3)
            ans="<" if a/b < dec else ">" if a/b > dec else "="
            return (f"Compare by inserting <, >, or =: ${a}/{b}\\;\\square\\;{dec}$.","multiple_choice",ans,"=",["<",">","="],_sol("Compare equivalent real values.","fraction vs decimal",[f"{a}/{b}≈{a/b:.3f}",f"Therefore {ans}."],ans,"Check on a number line."),"classification",{})
        if k == 1:
            a,b=sorted(rng.sample(range(1,10),2))
            return (f"Which is greater: $-{a}$ or $-{b}$?","multiple_choice",f"-{a}",f"-{b}",[f"-{a}",f"-{b}","equal"],_sol("On the negative side, the number closer to zero is greater.","negative ordering",[f"-{a}>-{b}"],f"-{a}","Check positions on a number line."),"verbal",{})
        if k == 2:
            a=rng.randint(2,9)
            return (rf"Evaluate exactly: $|-|{-a}||$.","integer",str(a),str(-a),[],_sol("Absolute value is nonnegative distance from zero.","nested absolute value",[f"|-{a}|={a}",f"|{a}|={a}"],str(a),"Result must be nonnegative."),"symbolic",{})

    if fid == "CH1-RATIONALIZE-DENOMINATOR":
        q=next(v for v in range(rng.randint(2,10),20) if not sympy.integer_nthroot(v,2)[1])
        if k == 0:
            n=rng.randint(1,5); ans=f"{n}*sqrt({q})/{q}"
            return (rf"Rationalize and simplify: $\\frac{{{n}}}{{\\sqrt{{{q}}}}}$.","expression",ans,f"{n}/sqrt({q})",[],_sol("Multiply by the radical over itself.","single radical denominator",[rf"\\frac{{{n}\\sqrt{{{q}}}}}{{{q}}}"],ans,"Denominator is rational."),"symbolic",{})
        a=rng.randint(2,6)
        if a*a==q: a+=1
        den=a*a-q
        ans=f"({a}-sqrt({q}))/{den}"
        return (rf"Rationalize the denominator: $\\frac{{1}}{{{a}+\\sqrt{{{q}}}}}$.","expression",ans,"1",[],_sol("Use the conjugate of a binomial radical denominator.","conjugate denominator",[rf"\\frac{{{a}-\\sqrt{{{q}}}}}{{{a*a}-{q}}}"],ans,"Conjugate product is rational."),"symbolic",{})

    if fid == "CH1-RATIONAL-SIMPLIFY":
        a,b=rng.sample(range(2,9),2)
        if k == 0:
            prompt=rf"Simplify and preserve the original restriction: $\\frac{{x^2-{a*a}}}{{x-{a}}}$"; ans=f"x+{a}"
            steps=[f"(x-{a})(x+{a})/(x-{a})",f"x+{a}, x≠{a}"]
        else:
            prompt=rf"Fully simplify: $\\frac{{(x-{a})(x+{a})(x-{b})}}{{(x-{a})(x-{b})}}$ and list all excluded values from the original expression."; ans=f"x+{a}"
            steps=[f"Cancel common factors only after recording x≠{a},{b}.",ans]
        return (prompt,"expression",ans,"x",[],_sol("Factor/cancel factors while preserving original exclusions.",prompt,steps,ans,"Original denominator restrictions remain."),"symbolic",{"requires_domain_check":True,"requires_factoring":True})

    if fid == "CH1-RATIONAL-COMBINE":
        a,b=rng.sample(range(2,8),2)
        if k%2==0:
            prompt=rf"Combine into one rational expression: $\\frac{{1}}{{x-{a}}}+\\frac{{1}}{{x-{b}}}$"; ans=f"(2*x-{a+b})/((x-{a})*(x-{b}))"
        else:
            # 1/(x-a) - 1/(x-b) + 1/((x-a)(x-b))
            prompt=rf"Simplify into one rational expression: $\\frac{{1}}{{x-{a}}}-\\frac{{1}}{{x-{b}}}+\\frac{{1}}{{(x-{a})(x-{b})}}$"
            ans=f"({a-b+1})/((x-{a})*(x-{b}))"
        return (prompt,"expression",ans,"0",[],_sol("Use a complete LCD and combine only numerators.",prompt,[f"LCD=(x-{a})(x-{b})",f"Result={ans}"],ans,f"Check x≠{a},{b}."),"symbolic",{"requires_domain_check":True,"requires_factoring":True})

    if fid == "CH1-RATIONAL-DIVIDE":
        a,b=rng.sample(range(2,8),2)
        if k%2==0:
            prompt=rf"Simplify: $\\frac{{x^2-{a*a}}}{{x-{b}}}\\div\\frac{{x-{a}}}{{x+{b}}}$"; ans=f"(x+{a})*(x+{b})/(x-{b})"
        else:
            prompt=rf"Divide and simplify fully: $\\frac{{(x-{a})(x+{a})}}{{(x-{b})(x+{b})}}\\div\\frac{{x-{a}}}{{x+{b}}}$"; ans=f"(x+{a})/(x-{b})"
        return (prompt,"expression",ans,"x",[],_sol("Invert the divisor, factor, and cancel factors.",prompt,["Rewrite as multiplication by the reciprocal.",f"Result={ans}"],ans,"Keep restrictions from both original rational expressions and the divisor."),"symbolic",{"requires_domain_check":True,"requires_factoring":True})

    if fid == "CH1-RATIONALIZE-NUMERATOR":
        a=rng.randint(2,6)
        if k%2==0:
            c=rng.randint(2,8); prompt=rf"Rationalize the numerator: $\\frac{{\\sqrt{{x+{c}}}-\\sqrt x}}{{{c}}}$"; ans=f"1/(sqrt(x+{c})+sqrt(x))"
        else:
            prompt=rf"Rationalize the numerator and simplify: $\\frac{{\\sqrt x-{a}}}{{x-{a*a}}}$"; ans=f"1/(sqrt(x)+{a})"
        return (prompt,"expression",ans,"1",[],_sol("Multiply by the conjugate and use a difference of squares.",prompt,[f"Result={ans}"],ans,"Multiply back by the conjugate identity."),"symbolic",{})

    if fid == "CH2-RATIONAL-EQUATIONS":
        a,b=rng.sample(range(1,7),2)
        if k==0:
            sol=a+b; prompt=rf"State the domain, then solve: $\\frac{{1}}{{x-{a}}}=\\frac{{1}}{{{b}}}$"; ans=str(sol)
        elif k==1:
            sol=a+b+1; rhs=Fraction(1,sol-a)+Fraction(1,sol-b)
            prompt=rf"Find all real solutions: $\\frac{{1}}{{x-{a}}}+\\frac{{1}}{{x-{b}}}={rhs.numerator}/{rhs.denominator}$"; ans=str(sol)
        elif k==2:
            prompt=rf"Solve over the reals: $\\frac{{1}}{{x-{a}}}=0$"; ans="no solution"
        else:
            prompt=rf"Classify the equation on its original domain: $\\frac{{x-{a}}}{{x-{a}}}=1$"; ans="all real numbers"
            # validator cannot encode R\{a}; ask classification instead
            return (prompt,"multiple_choice","identity on its domain","contradiction",["identity on its domain","contradiction","conditional"],_sol("Simplify only after recording x≠a.",prompt,[f"For x≠{a}, both sides equal 1."],"identity on its domain",f"x={a} remains excluded."),"classification",{"requires_domain_check":True})
        return (prompt,"solution_set",ans,str(a),[],_sol("Clear denominators only after recording restrictions.",prompt,[f"Restrictions include x≠{a}" if k!=2 else f"x≠{a}",f"Solution: {ans}"],ans,"Check in the original rational equation."),"symbolic",{"requires_domain_check":True})

    if fid == "CH2-MIXTURE":
        if k==0:
            q=rng.choice([20,30,40,50,60]); prompt=f"A {q}-liter mixture must be 35% concentrate using 20% and 50% solutions. How many liters of the 50% solution are needed?"; ans=f"{q/2:.1f}"
            steps=[f"0.50x+0.20({q}-x)=0.35({q})",f"x={q/2:.1f}"]
        elif k==1:
            scores=[rng.randint(65,90) for _ in range(3)]; target=rng.randint(75,88); ans=str(4*target-sum(scores))
            prompt=f"A student has three equally weighted test scores {scores}. What fourth score gives an average of {target}?"; steps=[f"({'+'.join(map(str,scores))}+x)/4={target}",f"x={ans}"]
        else:
            adult,child,total=rng.randint(10,16),rng.randint(5,9),rng.choice([1000,1200,1500]); n=rng.choice([80,100,120]); # solve a*x+c(n-x)=total
            # rebuild total to exact sensible
            xsol=rng.randint(20,n-20); total=adult*xsol+child*(n-xsol); ans=str(xsol)
            prompt=f"At an event, {n} tickets were sold. Adult tickets cost ${adult} and student tickets ${child}. Revenue was ${total}. How many adult tickets were sold?"; steps=[f"{adult}x+{child}({n}-x)={total}",f"x={ans}"]
        return (prompt,"decimal" if "." in ans else "integer",ans,"0",[],_sol("Translate the weighted/conservation relationship into one equation.",prompt,steps,ans,"Check totals and units."),"context",{"requires_interpretation":True,"requires_multiple_methods":True})

    if fid == "CH2-FORMULA-REARRANGE":
        if k==0: prompt=r"Solve $A=P(1+rt)$ for $r$."; ans="(A/P-1)/t"; steps=["A/P=1+rt","r=(A/P-1)/t"]
        elif k==1: prompt=r"Solve $d=rt$ for $t$."; ans="d/r"; steps=["Divide both sides by r.","t=d/r"]
        elif k==2: prompt=r"Solve $I=Prt$ for $P$."; ans="I/(r*t)"; steps=["Divide both sides by rt.","P=I/(rt)"]
        else: prompt=r"Solve $y=mx+b$ for $m$."; ans="(y-b)/x"; steps=["y-b=mx","m=(y-b)/x"]
        return (prompt,"expression",ans,"0",[],_sol("Use inverse operations symbolically and keep the requested variable isolated.",prompt,steps,ans,"Substitute the rearranged expression into the original formula."),"symbolic",{"requires_multiple_methods":True})

    if fid == "CH2-QUADRATIC-TYPE":
        if k%2==0:
            prompt=r"Find all real solutions: $x^4-5x^2+4=0$."; ans="-2,-1,1,2"; steps=["Let u=x^2.","u^2-5u+4=0.","u=1 or 4; back-substitute."]
        else:
            prompt=r"Find all positive real solutions: $x+\\frac1x=\\frac52$."; ans="1/2,2"; steps=["Multiply by 2x.","2x^2-5x+2=0.","Factor and retain positive roots."]
        return (prompt,"solution_set",ans,"1,4",[],_sol("Expose a quadratic structure through substitution or clearing a reciprocal.",prompt,steps,ans,"Check candidates in the original equation."),"symbolic",{"requires_multiple_methods":True,"requires_factoring":True})

    if fid == "CH2-ABS-EQUATIONS":
        a=rng.randint(2,8); h=rng.randint(-5,5)
        if k==0: prompt=rf"Find all real solutions: $|x-{h}|={a}$."; ans=f"{h-a},{h+a}"
        elif k==1: prompt=rf"Solve: $2|x-{h}|+3={2*a+3}$."; ans=f"{h-a},{h+a}"
        else: prompt=rf"Solve over the reals: $|x-{h}|=-{a}$."; ans="no solution"
        return (prompt,"solution_set",ans,"0",[],_sol("Isolate the absolute value, then branch only when the target is nonnegative.",prompt,[f"Result: {ans}"],ans,"Substitute any candidates."),"symbolic",{})

    if fid == "CH2-RADICAL-EQUATIONS":
        a=rng.randint(1,6)
        if k%2==0:
            sol=rng.randint(a+1,a+8); c=sol-a; prompt=rf"Solve and check: $\\sqrt{{x-{a}}}={int(math.isqrt(c)) if int(math.isqrt(c))**2==c else 'sqrt('+str(c)+')'}$."
            # force perfect square
            t=rng.randint(2,5); sol=a+t*t; prompt=rf"Solve and check: $\\sqrt{{x-{a}}}={t}$."; ans=str(sol)
        else:
            t=rng.randint(2,5); sol=t*t; prompt=rf"Find all real solutions and check for extraneous values: $\\sqrt{{x}}+\\sqrt{{x}}={2*t}$."; ans=str(sol)
        return (prompt,"solution_set",ans,"0",[],_sol("Isolate radicals before squaring; every candidate must be checked.",prompt,[f"Solution candidate: {ans}"],ans,"Substitute in the original radical equation."),"symbolic",{"requires_extraneous_check":True})

    if fid == "CH2-COMPOUND-INEQUALITY":
        a=rng.randint(2,5); lo,hi=sorted(rng.sample(range(-8,9),2))
        if k%2==0:
            prompt=f"Solve and write interval notation: ${lo} < {a}x+1 <= {hi}$."; L=Fraction(lo-1,a); H=Fraction(hi-1,a); ans=f"({L},{H}]"
        else:
            prompt=f"Solve and write interval notation: ${lo} <= 1-{a}x < {hi}$."; # lo<=1-ax<hi -> (1-hi)/a < x <= (1-lo)/a
            L=Fraction(1-hi,a); H=Fraction(1-lo,a); ans=f"({L},{H}]"
        return (prompt,"interval",ans,"(-oo,oo)",[],_sol("Solve both bounds together and reverse inequalities when dividing by a negative.",prompt,[f"Answer {ans}"],ans,"Test a point from the interval."),"symbolic",{})

    if fid == "CH2-ABS-INEQUALITY":
        a=rng.randint(2,7); h=rng.randint(-4,4)
        if k==0: prompt=rf"Solve: $|x-{h}|<{a}$."; ans=f"({h-a},{h+a})"
        elif k==1: prompt=rf"Solve: $|x-{h}|>={a}$."; ans=f"(-oo,{h-a}] U [{h+a},oo)"
        else: prompt=rf"Solve: $|2x-{2*h}|<={2*a}$."; ans=f"[{h-a},{h+a}]"
        return (prompt,"interval",ans,"(-oo,oo)",[],_sol("Interpret absolute value as distance: inside for <, outside for >.",prompt,[f"Answer {ans}"],ans,"Test an interior/exterior point."),"symbolic",{})

    if fid == "CH2-POLYNOMIAL-INEQUALITY":
        a,b=sorted(rng.sample(range(-5,6),2))
        if k==0: prompt=rf"Solve: $(x-{a})(x-{b})>0$."; ans=f"(-oo,{a}) U ({b},oo)"
        elif k==1: prompt=rf"Solve: $(x-{a})^2(x-{b})<=0$."; ans=f"(-oo,{b}]" if a>b else f"(-oo,{b}]" # even factor doesn't change sign; if a maybe zero included already
        else: prompt=rf"Solve: $(x-{a})(x-{b})(x-{b-2})<0$."; roots=sorted([a,b,b+2]); ans=f"(-oo,{roots[0]}) U ({roots[1]},{roots[2]})"
        return (prompt,"interval",ans,"(-oo,oo)",[],_sol("Use zeros/multiplicity to build a sign chart.",prompt,[f"Critical values determine {ans}"],ans,"Test one point per interval."),"symbolic",{"requires_factoring":True})

    if fid == "CH2-RATIONAL-INEQUALITY":
        a,b=sorted(rng.sample(range(-4,7),2))
        if k==0: prompt=rf"Solve: $\\frac{{x-{a}}}{{x-{b}}}>0$."; ans=f"(-oo,{a}) U ({b},oo)"
        elif k==1:
            c=b+2; prompt=rf"Solve: $\\frac{{(x-{a})(x-{c})}}{{x-{b}}}>=0$."; # sign intervals roots a<b<c assuming sorted a<b, c>b
            ans=f"[{a},{b}) U [{c},oo)"
        else:
            prompt=rf"Solve using the original domain: $\\frac{{(x-{a})(x-{b})}}{{x-{b}}}<0$."; ans=f"(-oo,{a})" if a<b else f"(-oo,{a})"
        return (prompt,"interval",ans,"(-oo,oo)",[],_sol("Separate numerator zeros from denominator exclusions and test signs.",prompt,[f"Answer {ans}"],ans,"Denominator zeros never enter the solution."),"symbolic",{"requires_domain_check":True,"requires_factoring":True})

    if fid == "CH3-PERP-BISECTOR":
        if k==0:
            # segment (0,0)-(4,0), point (2,p)
            p=rng.randint(1,6); prompt=f"Determine, with working, whether P=(2,{p}) lies on the perpendicular bisector of A=(0,0), B=(4,0)."; ans="yes"
            return (prompt,"multiple_choice",ans,"no",["yes","no"],_sol("Points on a perpendicular bisector are equidistant from endpoints.",prompt,[f"PA^2=4+{p*p}=PB^2"],ans,"Equal squared distances verify it."),"verbal",{"requires_interpretation":True})
        if k==1:
            prompt="Find the equation of the perpendicular bisector of the segment joining (0,0) and (4,2)."; ans="y=-2*x+5"
            return (prompt,"equation",ans,"y=2*x+1",[],_sol("Use midpoint and negative reciprocal slope.",prompt,["Midpoint=(2,1).","Segment slope=1/2, perpendicular slope=-2.","y-1=-2(x-2)."],ans,"Midpoint satisfies the line."),"symbolic",{"requires_multiple_methods":True})

    if fid == "CH4-BUILD-POLYNOMIAL":
        r1,r2=rng.sample(range(-4,5),2)
        if k==0:
            prompt=f"Find the monic quadratic polynomial with zeros {r1} and {r2}."; ans=str(sympy.expand((x-r1)*(x-r2)))
        elif k==1:
            # A factors and f(0)=target
            target=(0-r1)*(0-r2)*2; prompt=f"Find a quadratic polynomial with zeros {r1},{r2} and f(0)={target}."; ans=str(sympy.expand(2*(x-r1)*(x-r2)))
        else:
            prompt=f"Find the monic cubic polynomial whose zeros are {r1} (multiplicity 2) and {r2}."; ans=str(sympy.expand((x-r1)**2*(x-r2)))
        return (prompt,"expression",ans,"x",[],_sol("Convert each zero c to factor x-c; use multiplicity/scale data.",prompt,[f"Result={ans}"],ans,"Evaluate at roots and any scale condition."),"symbolic",{"requires_factoring":True})

    if fid == "CH4-POLY-SIGN-GRAPH":
        a,b=sorted(rng.sample(range(-4,5),2))
        if k==0: prompt=rf"For $f(x)=(x-{a})(x-{b})$, find the intervals where $f(x)>0$."; ans=f"(-oo,{a}) U ({b},oo)"
        elif k==1: prompt=rf"For $f(x)=(x-{a})^2(x-{b})$, find the intervals where $f(x)<0$."; ans=f"(-oo,{b})" if a>b else f"(-oo,{b})"
        else:
            c=b+2; prompt=rf"For $f(x)=(x-{a})(x-{b})(x-{c})$, find where $f(x)>0$."; ans=f"({a},{b}) U ({c},oo)"
        return (prompt,"interval",ans,"(-oo,oo)",[],_sol("Zeros, multiplicities and leading sign determine polynomial sign intervals.",prompt,[f"Answer {ans}"],ans,"Test one point per interval."),"graph",{"requires_graph":True,"requires_factoring":True})

    if fid == "CH4-IVT":
        if k==0:
            prompt="For f(x)=x^3-x-1, does the Intermediate Value Theorem guarantee a root in (1,2)?"; ans="yes"; steps=["f(1)=-1, f(2)=5; signs differ."]
        elif k==1:
            prompt="For f(x)=x^2+1, does the Intermediate Value Theorem guarantee a root in (-1,1) from endpoint signs?"; ans="no"; steps=["f(-1)=2 and f(1)=2; no sign change."]
        else:
            prompt="For f(x)=x^3, does IVT guarantee some c in (1,2) with f(c)=4?"; ans="yes"; steps=["f(1)=1<4<8=f(2)."]
        return (prompt,"multiple_choice",ans,"no" if ans=="yes" else "yes",["yes","no"],_sol("Continuous polynomials attain every intermediate value between endpoint outputs.",prompt,steps,ans,"Compare target with endpoint values."),"verbal",{"requires_interpretation":True})

    if fid == "CH5-INVERSE-DOMAIN-RANGE":
        a,c=rng.choice([2,3,4]),rng.choice([2,3,5]); b,d=rng.randint(-5,5),rng.randint(1,6)
        # ensure determinant nonzero
        if a*d-b*c==0: d+=1
        x_ex=Fraction(-d,c); y_ex=Fraction(a,c)
        if k%2==0:
            prompt=rf"Find the domain of $f(x)=\\frac{{{a}x+{b}}}{{{c}x+{d}}}$ in interval notation."; ans=f"(-oo,{x_ex}) U ({x_ex},oo)"
        else:
            prompt=rf"A one-to-one function is $f(x)=\\frac{{{a}x+{b}}}{{{c}x+{d}}}$. Use inverse reasoning to find its range."; ans=f"(-oo,{y_ex}) U ({y_ex},oo)"
        return (prompt,"interval",ans,"(-oo,oo)",[],_sol("Domain excludes denominator zero; range excludes the inverse's denominator zero.",prompt,[f"Excluded value gives {ans}"],ans,"Check by solving y=f(x) for x."),"symbolic",{"requires_domain_check":True,"requires_multiple_methods":True})

    if fid == "CH5-EXP-MODEL":
        if k==0:
            p=rng.randint(20,60); b=2; t=rng.randint(2,5); val=p*b**t; prompt=f"A population is {p} at t=0 and doubles each period. Write P(t)=ab^t and find P({t})."; ans=str(val)
        elif k==1:
            p=rng.randint(200,800); b=Fraction(4,5); t=3; val=Fraction(p*64,125); prompt=f"A quantity begins at {p} and is multiplied by 0.8 each year. Find its value after 3 years."; ans=f"{float(val):.3f}"
            return (prompt,"decimal",ans,"0",[],_sol("Use y=ab^t with decay factor 0.8.",prompt,[f"{p}(0.8)^3={ans}"],ans,"Value should be smaller than the initial amount."),"context",{"requires_interpretation":True})
        else:
            p=rng.randint(10,30); t=4; val=p*(1.05**t); prompt=f"An index is {p} at t=0 and grows 5% per period. Predict it at t=4."; ans=f"{val:.3f}"
            return (prompt,"decimal",ans,"0",[],_sol("Convert percent growth to factor 1.05.",prompt,[f"{p}(1.05)^4={ans}"],ans,"Growth result exceeds the initial value."),"context",{"requires_interpretation":True})
        return (prompt,"integer",ans,"0",[],_sol("Use y=ab^t and identify initial value and growth factor.",prompt,[f"Result={ans}"],ans,"Check direction of growth/decay."),"context",{"requires_interpretation":True})

    if fid == "CH5-EXP-FROM-FEATURES":
        if k%2==0:
            a,b,c=rng.randint(1,4),2,rng.randint(-3,3); y0=a+c
            prompt=f"Find an exponential function of the form f(x)=a*2^x+c with horizontal asymptote y={c} and y-intercept {y0}."; ans=f"{a}*2^x+({c})"
        else:
            a,c=rng.randint(1,4),rng.randint(-3,3); prompt=f"Find an exponential function with horizontal asymptote y={c}, passing through (0,{a+c}), and decreasing with base 1/2."; ans=f"{a}*(1/2)^x+({c})"
        return (prompt,"expression",ans,"2^x",[],_sol("Use asymptote for vertical shift and the y-intercept for scale.",prompt,[f"Result={ans}"],ans,"Evaluate at x=0 and inspect asymptote."),"graph",{"requires_interpretation":True})

    if fid == "CH5-CONTINUOUS-COMPOUND":
        P0=rng.choice([1000,2000,5000]); r=0.05
        if k==0:
            t=3; ans=f"{P0*math.exp(r*t):.2f}"; prompt=f"${P0} is invested at 5% compounded continuously. Find the amount after {t} years."
            return (prompt,"decimal",ans,"0",[],_sol("Use A=Pe^(rt).",prompt,[f"A={P0}e^(.05*{t})={ans}"],ans,"Amount exceeds principal for positive rate."),"context",{"requires_interpretation":True})
        if k==1:
            A=P0*2; ans=f"{math.log(2)/r:.3f}"; prompt=f"At 5% continuous growth, how long does it take ${P0} to double?"
            return (prompt,"decimal",ans,"0",[],_sol("Solve A=Pe^(rt) for t using ln.",prompt,["2=e^(0.05t)",f"t=ln(2)/.05={ans}"],ans,"Substitute time back into the model."),"context",{"requires_multiple_methods":True,"requires_interpretation":True})

    if fid == "CH5-LOG-EQUAL":
        a=rng.randint(2,8)
        if k==0:
            prompt=rf"Solve and check the log domain: $\\ln(x-{a})=\\ln 5$."; ans=str(a+5)
        elif k==1:
            # ln(x-3)=ln(-x+5) -> x=4 valid
            prompt=r"Solve and check: $\\ln(x-3)=\\ln(5-x)$."; ans="4"
        else:
            prompt=r"Solve over the reals: $\\ln(x-2)=\\ln(1-x)$."; ans="no solution"
        return (prompt,"solution_set",ans,"0",[],_sol("Equal logs have equal positive arguments; domain checks are mandatory.",prompt,[f"Result {ans}"],ans,"Every original log argument must be >0."),"symbolic",{"requires_domain_check":True,"requires_extraneous_check":True})

    if fid == "CH5-LOG-GRAPH":
        if k==0:
            prompt=r"What is the domain of $y=\\log_2(x-3)$?"; ans="(3,oo)"
            return (prompt,"interval",ans,"(-oo,oo)",[],_sol("A logarithm argument must be positive.",prompt,["x-3>0"],ans,"Vertical asymptote is x=3."),"graph",{"requires_domain_check":True})
        if k==1:
            prompt=r"The graph of $y=2^x$ contains (3,8). Which point must lie on $y=\\log_2 x$?"; ans="8,3"
            return (prompt,"ordered_pair",ans,"3,8",[],_sol("Inverse graphs swap coordinates.",prompt,["(3,8) becomes (8,3)."],ans,"Reflect across y=x."),"graph",{"requires_interpretation":True})
        prompt=r"For $y=\\log_{1/2}(x)$, is the function increasing or decreasing?"; ans="decreasing"
        return (prompt,"multiple_choice",ans,"increasing",["increasing","decreasing"],_sol("Logarithm with base between 0 and 1 is decreasing.",prompt,[ans],ans,"Compare with inverse exponential decay."),"graph",{"requires_interpretation":True})

    if fid == "CH5-LOG-PROPERTY-EQUATION":
        if k==0:
            prompt=r"Solve: $\\ln x+\\ln(x-3)=\\ln 4$."; ans="4"; steps=["ln(x(x-3))=ln4","x^2-3x-4=0","x=4 after domain check"]
        elif k==1:
            prompt=r"Solve: $2\\ln x=\\ln 9$."; ans="3"; steps=["ln(x^2)=ln9","x^2=9","x>0 so x=3"]
        else:
            prompt=r"Solve: $\\ln(x+1)-\\ln x=\\ln 2$."; ans="1"; steps=["ln((x+1)/x)=ln2","x+1=2x","x=1"]
        return (prompt,"solution_set",ans,"-3",[],_sol("Condense logs, use one-to-one behavior, then check positive arguments.",prompt,steps,ans,"Check every log argument."),"symbolic",{"requires_domain_check":True,"requires_multiple_methods":True})

    if fid == "CH5-EXP-LOG-SOLVE":
        base=rng.choice([2,3,5])
        if k==0:
            c=rng.randint(5,20); prompt=rf"Solve exactly: ${base}^x={c}$."; ans=f"log({c})/log({base})"
        elif k==1:
            prompt=r"Solve exactly: $2^{x+1}=3^{x}$."; ans="-log(2)/(log(2)-log(3))"
        else:
            prompt=rf"Find all real $x$: ${base}^{{x^2}}={base**4}$."; ans="-2,2"
            return (prompt,"solution_set",ans,"4",[],_sol("Use one-to-one behavior after matching bases.",prompt,["x^2=4","x=±2"],ans,"Substitute both roots."),"symbolic",{"requires_multiple_methods":True})
        return (prompt,"expression",ans,"0",[],_sol("Take logarithms and use the log power rule.",prompt,[f"Result={ans}"],ans,"Exponentiate/check numerically."),"symbolic",{"requires_multiple_methods":True})

    if fid == "CH5-EXP-MIXED-SUBSTITUTION":
        base=rng.choice([2,3,5])
        if k==0:
            prompt=rf"Solve for real $x$: ${base}^x+{base}^{{-x}}=\\frac52$."; ans="-1,1" if base==2 else f"-log(2)/log({base}),log(2)/log({base})"
        elif k==1:
            # u^2-5u+4=0, u=b^x -> u=1,4
            prompt=rf"Solve: ${base}^{{2x}}-5{base}^x+4=0$."; ans=f"0,log(4)/log({base})"
        else:
            # u^2+u-2=0 => u=1 or -2 reject
            prompt=rf"Solve over the reals: ${base}^{{2x}}+{base}^x-2=0$."; ans="0"
        return (prompt,"solution_set",ans,"-2",[],_sol(f"Let u={base}^x>0 and solve the resulting quadratic.",prompt,["Solve in u.","Reject u≤0.","Back-substitute."],ans,"Check positive exponential values."),"symbolic",{"requires_multiple_methods":True})


    if fid == "CH3-FUNCTION-PARITY":
        if k == 0:
            prompt=r"Classify $f(x)=x^4+3x^2-2$ as even, odd, or neither."; ans="even"
            steps=[r"f(-x)=(-x)^4+3(-x)^2-2=f(x)."]
        elif k == 1:
            prompt=r"Classify $g(x)=x^3-4x$ as even, odd, or neither."; ans="odd"
            steps=[r"g(-x)=-x^3+4x=-g(x)."]
        elif k == 2:
            prompt=r"Classify $h(x)=x^3+x^2$ as even, odd, or neither."; ans="neither"
            steps=[r"h(-x)=-x^3+x^2$, which is neither h(x) nor -h(x)."]
        else:
            prompt="A graph is symmetric about the y-axis. Classify the represented function as even, odd, or neither."; ans="even"
            steps=["y-axis symmetry is the graphical signature of an even function."]
        return (prompt,"multiple_choice",ans,"neither",["even","odd","neither"],_sol("Use f(-x)=f(x) for even and f(-x)=-f(x) for odd.",prompt,steps,ans,"Check algebraic or graphical symmetry."),"classification" if k<3 else "graph",{"requires_interpretation":k==3})

    if fid == "CH3-PIECEWISE-FUNCTION":
        if k == 0:
            prompt=r"Let $f(x)=\begin{cases}x+2,&x<1\\x^2,&x\ge1\end{cases}$. Find $f(-3)$."; ans="-1"
        elif k == 1:
            prompt=r"Let $f(x)=\begin{cases}2x,&x<2\\x+5,&x\ge2\end{cases}$. Find $f(2)$."; ans="7"
        elif k == 2:
            prompt=r"Let $f(x)=\begin{cases}x+1,&x<0\\3,&0\le x\le2\\x-1,&x>2\end{cases}$. On which interval is f constant?"; ans="[0,2]"
            return (prompt,"interval",ans,"(0,2)",[],_sol("Read the condition attached to each branch.",prompt,["The middle branch equals 3 for every x in [0,2]."],ans,"Endpoints are included by ≤."),"verbal",{"requires_interpretation":True})
        else:
            prompt=r"For $f(x)=\begin{cases}x^2,&x<0\\x+1,&x\ge0\end{cases}$, which branch determines $f(0)$?"; ans="x+1"
            return (prompt,"multiple_choice",ans,"x^2",["x^2","x+1"],_sol("The inequality condition chooses the branch before any calculation.",prompt,["0 satisfies x≥0, not x<0."],ans,"Evaluate with the selected branch."),"classification",{"requires_interpretation":True})
        return (prompt,"integer",ans,"0",[],_sol("Choose the branch whose condition contains the input, then evaluate only that formula.",prompt,[f"Result={ans}"],ans,"Check the input against the branch inequality."),"symbolic",{"requires_interpretation":True})

    if fid == "CH3-QUADRATIC-VERTEX":
        if k == 0:
            a=rng.choice([1,2,3]); h=rng.randint(-4,4); c=rng.randint(-5,6); expr=sympy.expand(a*(x-h)**2+c)
            prompt=f"Find the vertex of $f(x)={sympy.sstr(expr)}$."; ans=f"{h},{c}"
            return (prompt,"ordered_pair",ans,"0,0",[],_sol("Use h=-b/(2a), then k=f(h).",prompt,[f"Vertex=({h},{c})."],ans,"Substitute h into the original function."),"symbolic",{"requires_multiple_methods":True})
        if k == 1:
            h=rng.randint(-5,5); c=rng.randint(-6,6); a=rng.choice([-3,-2,-1,1,2,3]); prompt=rf"For $f(x)={a}(x-{h})^2+({c})$, state the axis of symmetry."; ans=f"x={h}"
            return (prompt,"equation",ans,"x=0",[],_sol("Vertex form a(x-h)^2+k has axis x=h.",prompt,[ans],ans,"The vertex lies on this vertical line."),"symbolic",{})
        if k == 2:
            h=rng.randint(-4,4); c=rng.randint(1,10); prompt=rf"For $f(x)=-2(x-{h})^2+{c}$, what is the maximum value of f?"; ans=str(c)
            return (prompt,"integer",ans,str(h),[],_sol("A negative leading coefficient opens downward, so the vertex gives the maximum.",prompt,[f"Maximum value={c}."],ans,"The squared term is never positive after multiplying by -2."),"verbal",{"requires_interpretation":True})
        h=rng.randint(-4,4); c=rng.randint(-5,5); expr=sympy.expand(2*(x-h)**2+c); ans=f"2*(x-{h})^2+({c})"; prompt=f"Write $f(x)={sympy.sstr(expr)}$ in vertex form."
        return (prompt,"expression",ans,str(expr),[],_sol("Complete the square or use the vertex coordinates.",prompt,[ans],ans,"Expand to recover the standard form."),"symbolic",{"requires_multiple_methods":True})

    if fid == "CH3-QUADRATIC-APPLICATION":
        if k % 2 == 0:
            # h(t) = -16(t-2)^2 + H
            H=rng.choice([64,80,96,112]); prompt=f"A projectile's height is $h(t)=-16(t-2)^2+{H}$. At what time does it reach maximum height?"; ans="2"
            return (prompt,"decimal",f"{2.0:.1f}","0",[],_sol("The vertex of the height model gives the maximum.",prompt,["Vertex time t=2."],"2.0","The leading coefficient is negative, so this is a maximum."),"context",{"requires_interpretation":True})
        # area x(20-x) max at 10, area100
        prompt="A rectangular pen uses 20 meters of fencing for two adjacent variable sides in the model A(x)=x(20-x). What is the maximum possible area?"; ans="100"
        return (prompt,"integer",ans,"10",[],_sol("Rewrite the quadratic or use its vertex.",prompt,["A(x)=-x^2+20x.","Vertex x=10.","A(10)=100."],ans,"The parabola opens downward."),"context",{"requires_interpretation":True,"requires_multiple_methods":True})

    return _build_raw_base(fid, rng, variant)


def generate_practice_problem(family_id: str, seed: int, variant: int = 0) -> PracticeProblem:
    if family_id not in FAMILY_SPECS:
        raise KeyError(f"Unknown canonical family: {family_id}")
    family = PROBLEM_FAMILY_INDEX[family_id]
    spec = FAMILY_SPECS[family_id]
    rng = random.Random((seed * 1315423911 + variant * 2654435761) & 0xFFFFFFFF)
    prompt, answer_type, answer, wrong, choices, solution, representation, flags = _build_raw(
        family_id, rng, variant
    )
    layer = _layer(variant)
    evidence = family_complexity_evidence(
        family_id,
        layer,
        representation=representation,
        variant_index=variant,
        solution_steps=max(1, len(solution.calculation)),
    )
    derived_layer = max(layer, complexity_layer(evidence), key=lambda l: int(l.value[1]))
    variant_type = family.structural_variants[variant % len(family.structural_variants)]
    sig = structural_signature(
        family_id,
        variant_type,
        representation,
        evidence.prerequisite_depth,
        evidence.decision_points,
        method_count=evidence.method_count,
        answer_form=answer_type,
    )
    refs = [f"{r.document}:{r.locator}" for r in family.source_refs]
    source_file = family.source_refs[0].document if family.source_refs else ""
    source_locator = family.source_refs[0].locator if family.source_refs else ""
    problem = PracticeProblem(
        problem_id=f"{family_id}-{seed}-{variant}",
        group=spec.group,
        chapter=spec.chapter,
        section=spec.section,
        family_id=family_id,
        family_title=family.title,
        difficulty=_difficulty_name(derived_layer),
        prompt=prompt,
        answer_type=answer_type,
        expected_answer=answer,
        wrong_answer=wrong,
        choices=choices,
        source_type="source-grounded-controlled-template",
        source_file=source_file,
        source_question_or_page=source_locator,
        construction_notes=(
            f"Canonical family {family_id}; structural variant '{variant_type}'. "
            "Numbers and surface wording may change; required concepts/procedures and checks remain invariant."
        ),
        rule_or_formula=solution.rule,
        required_skills=list(dict.fromkeys([*family.required_concepts, *family.required_procedures])),
        worked_solution=solution,
        parameter_seed=seed,
        difficulty_layer=derived_layer,
        representation=representation,
        source_refs=refs,
        variant_reason=variant_type,
        reasoning_checkpoints=list(dict.fromkeys([
            *family.recognition_features,
            *family.verification_methods,
        ])),
        complexity_level=derived_layer,
        decision_count=evidence.decision_points,
        prerequisite_count=evidence.prerequisite_depth,
        estimated_solution_steps=max(1, len(solution.calculation) + 1),
        representation_type=representation,
        structural_variant_type=variant_type,
        structural_signature=sig,
        application_context=application_context(family_id, variant),
        requires_domain_check=bool(flags.get("requires_domain_check")),
        requires_extraneous_check=bool(flags.get("requires_extraneous_check")),
        requires_factoring=bool(flags.get("requires_factoring")),
        requires_graph=bool(flags.get("requires_graph")),
        requires_interpretation=bool(flags.get("requires_interpretation")) or representation in {"context","graph","table","verbal","multipart"},
        requires_multiple_methods=bool(flags.get("requires_multiple_methods")) or evidence.method_count > 1,
        professor_grammar=_professor_grammar(family),
        complexity_evidence=evidence,
        source_exemplar_id=refs[0] if refs else "",
    )
    # A generator must never ship a self-invalid answer.
    validation = validate_practice_answer(problem, problem.expected_answer)
    if not validation.correct:
        raise ValueError(
            f"Generator produced an invalid expected answer for {family_id}: "
            f"{problem.expected_answer!r} ({validation.error_code})"
        )
    return problem


def generate_scope_problems(
    scopes: list[str], count: int, seed: int, *, start_variant: int = 0
) -> list[PracticeProblem]:
    pool: list[str] = []
    for scope in scopes:
        pool.extend(families_for_scope(scope))
    pool = list(dict.fromkeys(pool)) or list(FAMILY_SPECS)
    rng = random.Random(seed)
    rng.shuffle(pool)
    result: list[PracticeProblem] = []
    for index in range(count):
        fid = pool[index % len(pool)]
        cycle = index // len(pool)
        result.append(generate_practice_problem(fid, seed + index * 9973, start_variant + cycle + index))
    return result
