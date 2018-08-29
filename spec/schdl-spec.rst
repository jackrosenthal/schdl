ScHDL: The Scheme Inspired Hardware Description Language
========================================================

.. default-role:: math

ScHDL is a hardware description language that takes inspiration from the
algorithmic programming language Scheme. The language is created with the
following goals:

1. To create a minimal HDL, which only provides NAND and wires out of the box.
2. To allow easy abstraction of hardware-level concepts into nearly algorithmic
   language structures.

The primary intention of this language is to be used in a course, acting as a
replacement to the hardware description language used in the nand2tetris
course.

.. note::

   This language spec is made to serve two fold:

   1. It should be easy to read and learn the language from the spec, and
      additionally,
   2. It should present the reader with a "formal enough" definition to go and
      implement the language.

Syntax
------

The primary syntactic structure of ScHDL is s-expressions. To avoid redefining
the wheel, the reader is advised to read the `Wikipedia Page`_ on s-expressions
for an informal and easy introduction, or the `Racket Reader Specification`_
for a formalized account of the language's syntax.

.. _Wikipedia Page: https://en.wikipedia.org/wiki/S-expression
.. _Racket Reader Specification: https://docs.racket-lang.org/reference/reader.html

Semantics
---------

Fundamentally, ScHDL provides a single builtin hardware module, ``nand``. The
syntax for ``nand`` is:

.. parsed-literal::

   (nand `a` `b`) `\to` (named-outputs (out `\lnot (a \land b)`))

``named-outputs`` is the fundamental return type of hardware modules in ScHDL.
It allows hardware modules to have a single output, or multiple (named)
outputs, which is important to making the language feel algorithmic.

Outputs named ``out`` are assumed to be the default output of a hardware module
when their data is substituted into another module's input. When the syntax
``output`` is used, specific outputs from a ``named-outputs`` can be retrieved.

``named-outputs`` is covered in much greater detail later in this document.

Declaring Modules
~~~~~~~~~~~~~~~~~

Module declarations are done using the syntax ``define``:

.. parsed-literal::

   (define (`n` `a_0` `\cdots` `a_n`)
     `s_0`
     `\vdots`
     `s_n`)

This declares a module named `n` with input arguments `(a_0 \cdots a_n)` and
body `(s_0 \cdots s_n)`. Note that both the input arguments and the body may be
the empty list (``NIL``).

The input arguments may either be a single symbol (e.g., ``selector``), or a
list-matching specifier. A list-matching specifier is a single symbol followed
by a list-size specification in square brackets. This list-size specification
may be a constant integer, in which case the declaration will specify how the
name behaves when called with the exact number specified, or a single symbol,
in which case the declaration will apply to all inputs without a constant
integer declaration, and the specified symbol will be bound to the size of the
inputs at compile time.

If any part of the body at a top level is a ``named-outputs``, this will
specify the output of the module. Otherwise, the last non-declarative statement
in the body will become a ``named-outputs`` under the name ``out``. In the case
that the body is the empty list, the result will be a ``named-outputs`` with a
single output ``out`` with a value of the empty list.

Example: Not Gate
^^^^^^^^^^^^^^^^^

This is best seen by example rather than a technical explanation as given
above. For example, suppose we wanted to define the module ``not``, which acted
as a logical not gate. We could do so using the following declaration::

   (define (not in)
     (nand in in))

This defines the operation ``not`` for a single-wire input, but we may wish to
also define a bitwise ``not`` for a list of wires::

   ;; Defines not for a list of zero wires. This is empty, so it produces
   ;; a (named-outputs (out NIL))
   (define (not in[0]))

   ;; Defines not for a list of n wires.
   (define (not in[n])
     (cons (not (car in))   ;; this will use the not specified for
                            ;; a single wire

           (not (cdr in)))) ;; this will use this not implementation
                            ;; if n is not 1, or the zero-wire version
                            ;; if n is indeed 1

Example: Functional Abstractions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Being a primary goal of ScHDL to support algorithmic-style programming, it's
important to see how this syntax declaration leads to the ability to define
functional abstractions. A ``map`` "module" can be defined to support
functional mapping::

   ;; Semantics is similar to not example, but allows operation
   ;; on any function.
   (define (map f wires[0]))

   (define (map f wires[n])
     (cons (f (car wires))
           (map f (cdr wires))))

Note that in this case ``f`` is referred to by *name*, rather than being bound
to a singular module declaration. This will always be the case with treating
modules as data in ScHDL.

Given this, we can define a simpler version of a bitwise ``not``::

   (define (not in[n])
     (map not in))

Declaring Parts
~~~~~~~~~~~~~~~

``define`` has a second meaning when used in the following form:

.. parsed-literal::

   (define ``n`` ``e``)

In this case, this defines a name ``n`` to the expression ``e``. All names from
the enclosing scope will be visible within the scope of ``e`` as well, allowing
parts to be attached to themselves. This is particularly useful for declaring
parts in a module.

Example: Latch
^^^^^^^^^^^^^^

By allowing parts to refer to themselves, we can attach the output of a part to
one of its own inputs::

   (define (latch set reset)
     (define set-nand (nand (not set)
                            reset-nand))
     (define reset-nand (nand (not reset)
                              set-nand))
     (named-outputs
       (out set-nand)
       (not-out reset-nand)))

Example: Bit Register
^^^^^^^^^^^^^^^^^^^^^

This is a one-bit register using the ``latch`` implementation. If ``load`` is
high, then the value of the register will change to ``value``. Otherwise, the
register remains unchanged::

   (define (bit-register value load)
     ;; note that "and" has not been defined here, but is
     ;; assumed to have been defined by the user
     (define set (and load value))
     (define reset (and load (not value)))
     (define latch-value (latch set reset))

     ;; the output is simply the named-outputs of the latch
     latch-value)

Named Outputs
~~~~~~~~~~~~~

A named outputs has the following syntax:

.. parsed-literal::

   (named-outputs
     (`k_1` `v_1`)
     `\vdots`
     (`k_n` `v_n`))

Where `k_n` is the name of each output, and `v_n` is the value of the output.

A specific output from a ``named-outputs`` can be retrieved using the following
syntax:

.. parsed-literal::

   (output `k` `x`)

Where `k` is the name of the output, and `x` is the ``named-outputs``.

As stipulated previously, the compiler will implicitly construct
``named-outputs`` if one is not defined from the result of an evaluation, and
may implicitly insert ``(output out ...)`` syntax when a ``named-outputs`` is
passed as an input to a module.

Builtins
--------

Besides the fundamental ``nand``, ``named-outputs``, ``output``, and
``define``, the following **compile-time** builtins are available.

Constants
~~~~~~~~~

* ``NIL`` is the empty list
* ``#t`` is true
* ``#f`` is false

``#t`` can be connected to a part to bring a wire high.
``#f`` and ``NIL`` can be connected to a part to bring a wire low.

Macros
~~~~~~

* (``cons`` `a` `b`): Create a cons cell with `a` as CAR and `b` as CDR.
* (``car`` `c`): Get the CAR of a cons cell.
* (``cdr`` `c`): Get the CDR of a cons cell.
* (``list`` `a_0 \cdots a_n`): Equivalent to
  (``cons`` `a_0` (``cons`` `\cdots` (``cons`` `a_n` ``NIL``))).
* (``length`` `c`): Gets the length of a cons cell constructed list `c`.
* (``=`` `a` `b`): Compares if two compile-time comparable values are equal.
* ``<=``, ``>=``, ``<``, ``>``: same as above with alternate comparisons.
* (``if`` `p` `c` `a`): Return `c` if `p` otherwise `a`.
* (``when`` `p` `c`): Equivalent to (``if`` `p` `c` ``NIL``).
* (``unless`` `p` `a`): Equivalent to (``if`` `p` ``NIL`` `a`).
* (``cond`` (`p_1` `c_1`) `\cdots` (`p_n` `c_n`)): Return the first `c_n` for
  which `p_n` evaluates to true.
