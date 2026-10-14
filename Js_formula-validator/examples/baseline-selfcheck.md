# 对照基线：一次「让 LLM 自己反复推导检查」的样本

这份文件是成本对照用的**实测样本**，不是装饰。

内容是一次有代表性的 LLM 自查响应：验一条 4 步推导链
（相对论能量关系），包含逐步代数复核、量纲检查、极限检查与数值抽查。
写得克制，没有注水——这样对照不会高估基线。

下方 `---` 之间为样本正文，其字符数即测量对象。

---

Let me verify this chain step by step.

Chain:
  1. E^2 = (pc)^2 + (mc^2)^2
  2. E^2 = p^2 c^2 + m^2 c^4
  3. E = sqrt(p^2 c^2 + m^2 c^4)
  4. E = mc^2 (1 + p^2/(2 m^2 c^2))

**Step 1 → 2.** Expand both squares: (pc)^2 = p^2 c^2 and (mc^2)^2 = m^2 c^4. Correct.

**Step 2 → 3.** Take the positive square root, taking E > 0 for a free particle. Correct.

**Step 3 → 4.** This is where I need to be careful. Factor out m^2 c^4:

  sqrt(p^2 c^2 + m^2 c^4) = mc^2 sqrt(1 + p^2/(m^2 c^2))

Now, sqrt(1 + u) = 1 + u/2 - u^2/8 + ... is a Taylor series, **not an identity**.
Step 4 has replaced the square root by the first two terms of its expansion. So
step 4 is only the leading-order approximation in p/(mc), not an equality.

Let me confirm numerically. Take m = 1, c = 1, p = 1 (so p/(mc) = 1, far from the
non-relativistic regime where the expansion is valid):

  E (step 3) = sqrt(1 + 1) = 1.414214
  E (step 4) = 1 * (1 + 1/2) = 1.500000

They differ by about 6%, so the break is confirmed at step 4.

At p = 0.1 the two agree to about 1e-4, which is consistent with a truncation
error of order (p/mc)^4 — that is why the error is invisible in the
non-relativistic limit and easy to miss by inspection.

**Dimensional check.** p^2/(m^2 c^2) is dimensionless: [p^2] = kg^2 m^2 s^-2 and
[m^2 c^2] = kg^2 m^2 s^-2. So step 4 is dimensionally consistent and the
dimensional check alone would **not** catch this error. This is precisely the
class of mistake a dimension-only check misses.

**Limit check.** As p → 0, step 3 gives mc^2 and step 4 gives mc^2, so the limit
agrees — again the error hides near p = 0. As p → infinity, step 3 grows like pc
(linear) while step 4 grows like p^2/(2m) (quadratic), so the two diverge in
their asymptotics. Checking the large-p limit exposes the error; checking p → 0
does not.

**Conclusion.** The chain is correct through step 3. Step 4 wrongly promotes a
Taylor truncation to an equality; it holds only for p << mc. The correct
statement is E = mc^2 sqrt(1 + p^2/(m^2 c^2)), or, as an approximation,
E ≈ mc^2 + p^2/(2m) with the remainder bounded by p^4/(8 m^3 c^2).

---

## 测量

样本正文实测：

- **2106 字符**
- 折算 token：按 4.0 字符/token 得 **527**，按 3.5 得 602

后续计算一律取 **527**（即 4.0 折算），这是对工具**不利**的取法——基线估得
越小，省下的比例越难看。宁可低估自己的收益。

这是**一次**自查的成本。

关键在于：一次自查不足以建立信任——这整个工具存在的理由就是 LLM 会自信地
编造。实践中要得到可信结论，通常需要在独立上下文里重复 3 次，否则你只是在
用同一个可能出错的认知路径再走一遍。故基线取 3 × 527 ≈ **1581 token**。

对照：同一个 4 步链交给本工具，输出固定为 555 字符 ≈ 159 token，且**与推导
长度无关**（8 步链实测 556 字符，几乎不变）。

完整的对照表与三个测试用例见 `three-cases.md`。
