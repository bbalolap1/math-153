# Test 3 Review --- Human-Readable Markdown

**Date:** 08/06/2026\
**Name:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

## Format

Each problem preserves the **full question text** and shows important
mathematics in two forms:

1.  **Human-readable mathematics** --- standard rendered math inside the
    Markdown.
2.  **Computer-readable LaTeX** --- the same mathematical content in a
    code block.

No external images are required.

------------------------------------------------------------------------

## Q.1 --- Composite Functions

**Exercises 21--34:** Find:

1.  ((f `\circ `{=tex}g)(x)) and the domain of (f `\circ `{=tex}g)
2.  ((g `\circ `{=tex}f)(x)) and the domain of (g `\circ `{=tex}f)

### Exercise 21

**Human-readable**

\[ f(x)=x\^2-3x,`\qquad `{=tex}g(x)=`\sqrt{x+2}`{=tex} \]

**Computer-readable (LaTeX)**

``` latex
f(x)=x^2-3x,\qquad g(x)=\sqrt{x+2}
```

### Exercise 22

**Human-readable**

\[ f(x)=`\sqrt{x-15}`{=tex},`\qquad `{=tex}g(x)=x\^2+2x \]

**Computer-readable (LaTeX)**

``` latex
f(x)=\sqrt{x-15},\qquad g(x)=x^2+2x
```

------------------------------------------------------------------------

## Q.2 --- Cable Corrosion

A 100-foot-long cable of diameter 4 inches is submerged in seawater.
Because of corrosion, the surface area of the cable decreases at the
rate of (750`\text{ in}`{=tex}\^2) per year.

Express the diameter (d) of the cable as a function of time (t) (in
years).

*Disregard corrosion at the ends of the cable.*

**Human-readable mathematical information**

\[
L=100`\text{ ft}`{=tex},`\qquad `{=tex}d(0)=4`\text{ in}`{=tex},`\qquad`{=tex}
`\frac{\Delta S}{\Delta t}`{=tex}=-750`\text{ in}`{=tex}\^2/`\text{year}`{=tex}
\]

**Computer-readable (LaTeX)**

``` latex
L=100\text{ ft},\qquad d(0)=4\text{ in},\qquad
\frac{\Delta S}{\Delta t}=-750\text{ in}^2/\text{year}
```

------------------------------------------------------------------------

## Q.3 --- Domain and Range

The function

\[ f(x)=`\frac{2x-7}{9x+1}`{=tex} \]

is one-to-one.

1.  Find its domain.
2.  Find its range.

**Hint:** For the second part, remember that the range of (f(x)) is the
domain of (f\^{-1}(x)).

**Computer-readable (LaTeX)**

``` latex
f(x)=\frac{2x-7}{9x+1}

\operatorname{range}(f)=\operatorname{domain}(f^{-1})
```

------------------------------------------------------------------------

## Q.4 --- Car Loan

An automobile dealer offers customers no-down-payment 3-year loans at an
interest rate of 10%.

If a customer can afford to pay **\$500 per month**, find the price of
the most expensive car that can be purchased.

**Human-readable mathematical information**

\[ `\text{Loan term}`{=tex}=3`\text{ years}`{=tex},`\qquad`{=tex}
r=10%,`\qquad`{=tex} `\text{monthly payment}`{=tex}=\$500 \]

**Computer-readable (LaTeX)**

``` latex
\text{Loan term}=3\text{ years},\qquad
r=10\%,\qquad
\text{monthly payment}=\$500
```

------------------------------------------------------------------------

## Q.5 --- Consumer Price Index

The CPI is the most widely used measure of inflation.

In 1970, the CPI was 37.8, and in 2000, the CPI was 168.8. This means
that an urban consumer who paid \$37.80 for a market basket of consumer
goods and services in 1970 would have needed \$168.80 for similar goods
and services in 2000.

Find a simple exponential function of the form

\[ y=ab\^t \]

that models the CPI for 1970--2000, and predict its value for 2010.

**Computer-readable (LaTeX)**

``` latex
y=ab^t
```

------------------------------------------------------------------------

## Q.6 --- Exponential Equation

Find all real solutions to the equation

\[ e^{x^2}=e\^{7x-12}. \]

**Computer-readable (LaTeX)**

``` latex
e^{x^2}=e^{7x-12}
```

------------------------------------------------------------------------

## Q.7 --- Zeroes / Roots

Find all zeroes/roots of the function

\[ f(x)=4x^3e^{4x}+3x^2e^{4x}. \]

**Computer-readable (LaTeX)**

``` latex
f(x)=4x^3e^{4x}+3x^2e^{4x}
```

------------------------------------------------------------------------

## Q.8 --- Radioactive Iodine Decay

Radioactive iodine (\^{131}`\mathrm{I}`{=tex}) is frequently used in
tracer studies involving the thyroid gland.

The substance decays according to the formula

\[ A(t)=A_0a\^{-t}, \]

where (A_0) is the initial dose and (t) is the time in days.

Find (a), assuming the half-life of (\^{131}`\mathrm{I}`{=tex}) is 8
days.

**Computer-readable (LaTeX)**

``` latex
A(t)=A_0a^{-t}
```

------------------------------------------------------------------------

## Q.9 --- Logarithmic Equation

Find all real solutions to the equation

\[ `\log`{=tex}\_3(x+3)+`\log`{=tex}\_3(x+5)=1 \]

and check that they all make sense.

**Computer-readable (LaTeX)**

``` latex
\log_3(x+3)+\log_3(x+5)=1
```

------------------------------------------------------------------------

## Q.10 --- Exponential Equation

Find all real solutions to the equation

\[ 3^{2-3x}=4^{2x+1}. \]

**Computer-readable (LaTeX)**

``` latex
3^{2-3x}=4^{2x+1}
```

------------------------------------------------------------------------

## Q.11 --- Graphing

Sketch the graph of

\[ y=-x^3+3x^2+10x \]

on a coordinate grid.

**Computer-readable (LaTeX)**

``` latex
y=-x^3+3x^2+10x
```

------------------------------------------------------------------------

## Q.12 --- Polynomial Roots

\(k\) is some unknown constant.

If one zero/root of

\[ f(x)=x^3-2x^2-16x+16k \]

is (x=2), find all of (f(x))'s roots.

**Hint:** First find (k).

**Computer-readable (LaTeX)**

``` latex
f(x)=x^3-2x^2-16x+16k,\qquad x=2
```

------------------------------------------------------------------------

## Q.13 --- Polynomial Division

Find the quotient and remainder if

\[ 2x^3-10x^2+x-2 \]

is divided by

\[ 2x\^2+1. \]

**Computer-readable (LaTeX)**

``` latex
\frac{2x^3-10x^2+x-2}{2x^2+1}
```

------------------------------------------------------------------------

## Q.14 --- Factor Theorem

Show that (x-3) divides the polynomial

\[ 3x^3-10x^2+7x-12 \]

without doing polynomial long division.

**Computer-readable (LaTeX)**

``` latex
x-3\ \text{ divides }\ 3x^3-10x^2+7x-12
```
