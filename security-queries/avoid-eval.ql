
/**
 * @name Avoid dynamic evaluation
 * @description Detects calls to Python eval().
 * @kind problem
 * @problem.severity error
 * @security-severity 8.0
 * @precision high
 * @id securebank/avoid-eval
 * @tags security
 *       external/cwe/cwe-95
 */

import python

from Call call, Name name

where
    call.getFunc() = name and
    name.getId() = "eval"

select call,
    "Avoid eval() with untrusted or dynamically supplied input. Use a safe parser or explicit validation."
