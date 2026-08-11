# Completing the Square

> Human-readable Markdown conversion of the 3-page source. The source's
> terminology, order, formulas, and worked examples are preserved.

## General Formula

A general quadratic polynomial

\[ ax\^2+bx+c \]

has the completed-square form

\[ `\boxed{
a\left(x+\frac{b}{2a}\right)^2+c-\frac{b^2}{4a}
}`{=tex} \]

This formula always works. The source notes that, when using it, the
general formula should be stated for full credit, just as with the
quadratic formula.

Some books and websites use **vertex form**

\[ a(x-h)\^2+k, \]

where (h) and (k) are constants with their own formulas.

### Why complete the square?

The completed-square form collapses a quadratic polynomial with two
(x)-terms into:

-   one squared binomial involving (x), and
-   constants.

That squared binomial is easier to isolate in many equations.

------------------------------------------------------------------------

## Example 1 --- Write (3x\^2-15x+20) in Completed-Square Form

### Step 1

Factor the (x\^2)-coefficient out of the (x\^2) and (x) terms, but not
the constant:

\[ 3x\^2-15x+20 = 3(x\^2-5x)+20. \]

### Step 2

Inside the brackets, the coefficient of (x) is (-5).

Divide it by (2):

\[ -`\frac52`{=tex}. \]

Therefore the squared binomial will be

\[ `\left`{=tex}(x-`\frac52`{=tex}`\right`{=tex})\^2. \]

Write

\[ 3x\^2-15x+20 = 3`\left`{=tex}(x-`\frac52`{=tex}`\right`{=tex})\^2+d.
\]

### Step 3

Solve for (d) by expanding and comparing constant terms.

Recall:

\[ (a+b)^2=a^2+2ab+b\^2. \]

Then

\[ 3x\^2-15x+20 = 3`\left`{=tex}(x-`\frac52`{=tex}`\right`{=tex})\^2+d
\]

# \[

3`\left`{=tex}(x\^2-5x+`\frac{25}{4}`{=tex}`\right`{=tex})+d \]

# \[

3x\^2-15x+`\frac{75}{4}`{=tex}+d. \]

Compare constants:

\[ 20=`\frac{75}{4}`{=tex}+d \]

so

\[ `\boxed{d=\frac54}`{=tex}. \]

### Step 4

Therefore

\[ `\boxed{
3x^2-15x+20
=
3\left(x-\frac52\right)^2+\frac54
}`{=tex} \]

------------------------------------------------------------------------

## Finding the Roots from the Completed-Square Form

Solve

\[ 3x\^2-15x+20=0. \]

Use

\[ 3x\^2-15x+20 =
3`\left`{=tex}(x-`\frac52`{=tex}`\right`{=tex})\^2+`\frac54`{=tex}. \]

Then

\[ 3`\left`{=tex}(x-`\frac52`{=tex}`\right`{=tex})\^2+`\frac54`{=tex}=0
\]

\[ 3`\left`{=tex}(x-`\frac52`{=tex}`\right`{=tex})\^2=-`\frac54`{=tex}
\]

\[ `\left`{=tex}(x-`\frac52`{=tex}`\right`{=tex})\^2=-`\frac5{12}`{=tex}
\]

\[ x-`\frac52`{=tex} = `\pm`{=tex}`\sqrt{-\frac5{12}}`{=tex} \]

# \[

`\pm `{=tex}i`\sqrt{\frac5{12}}`{=tex}. \]

Thus

\[ `\boxed{
x=\frac52\pm i\sqrt{\frac5{12}}
}`{=tex} \]

or, as simplified in the source,

\[ `\boxed{
x=\frac52\pm\frac{i}{2}\sqrt{\frac53}
}`{=tex}. \]

------------------------------------------------------------------------

## Example 2 --- Write (-x\^2-6x+1) in Completed-Square Form

### Step 1

Factor (-1) out of the (x\^2) and (x) terms:

\[ -x\^2-6x+1 = -1(x\^2+6x)+1. \]

### Step 2

The coefficient of (x) inside the brackets is (6).

Divide by (2):

\[ 3. \]

Therefore

\[ -x\^2-6x+1 = -1(x+3)\^2+d. \]

### Step 3

Expand:

\[ -x\^2-6x+1 = -1(x+3)\^2+d \]

# \[

-1(x\^2+6x+9)+d \]

# \[

-x\^2-6x-9+d. \]

Compare constants:

\[ 1=-9+d \]

so

\[ `\boxed{d=10}`{=tex}. \]

### Step 4

Therefore

\[ `\boxed{
-x^2-6x+1
=
-(x+3)^2+10
}`{=tex} \]

------------------------------------------------------------------------

## Finding the Roots

Solve

\[ -x\^2-6x+1=0. \]

Substitute the completed-square form:

\[ -(x+3)\^2+10=0 \]

\[ -(x+3)\^2=-10 \]

\[ (x+3)\^2=10 \]

\[ x+3=`\pm`{=tex}`\sqrt{10}`{=tex} \]

\[ `\boxed{x=-3\pm\sqrt{10}}`{=tex}. \]
