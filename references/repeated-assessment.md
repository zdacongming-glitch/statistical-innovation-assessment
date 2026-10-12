**固定材料下的独立重复评分**

创新性数值评价默认执行五轮独立评分；完整四维审核在同一批轮次分别评价四个维度。原有创新三级、整数锚点、小数规则及可靠性缺陷限制不变。重复只改变执行和汇总方式，不把贡献之间或维度之间的成绩合并。

用户明确要求一次、其他次数或快速的非数值初步判断时遵从，并标明实际执行情况。没有足以定位的材料时不强行生成点分，也不因“需要五个数字”重复猜测。

**1．先冻结可复用的证据包**

先核对稿件版本与贡献清单，找出支撑主要结论的核心贡献及辅助贡献，保留它们的相互作用。每轮看到完整问题与贡献关系，不能仅凭孤立片段评价，也不能把拆分产生的重复内容多次计新。

证据包至少包含：稿件版本或文件摘要、实际提供的材料与核验范围、固定贡献编号、核心与辅助关系、最邻近原始工作及其可核查结论、具体差异、未核实之处、当前成果或明确的条件性情景。文献检索与事实核查先完成到当前任务需要的范围，再冻结材料；用户要求不检索时记录该限制。

为整个包分配 packet_id，建议使用包文件及清单的 SHA-256 或明确的版本标识。为评分协议分配 protocol_id，关联规则版本、引用的锚点与示例、实际模型标识、可获知的快照、可控设置、评价范围和追加规则。同批中不能改变材料、模型、规则、提问方式或情景。

当前贡献与不同未来技术路线分别建对象或批次，不混算。只有区间判断时保持区间，并记录为什么没有点分；不能取中点来制造重复样本。

**2．真实执行五轮，隔离评分上下文**

优先使用运行环境提供的隔离评估子代理；本 skill 明确允许为这些评分轮次进行此项委派。每个代理使用同一证据包、完整的相关评分标准和同一任务，保持相同模型及实际可控设置，并按并发能力分批执行。不要继承含有历史成绩、其他轮次结论或投稿排名的对话；能选择上下文继承方式时使用空白上下文并显式提供材料。

如果环境已有可用且获授权的独立模型调用，也可以使用单独的新上下文请求；本流程本身不要求接入 API 或创建密钥。记录实际工具或 API 返回的执行标识、上下文／请求标识和可获知的模型设置，不能只生成随机 ID 就声称调用发生。

每轮都先判断贡献性质和升级门槛，再给一位小数成绩及简短的证据依据；不要求输出隐藏的内部推理。每轮输出逐项创新评价及整篇创新性，整篇按支撑主要结论的核心贡献判断，不能由脚本计算各贡献均分。完整审稿时每轮还分别输出三个其他维度，并给可靠性的核验范围与缺陷状态。

所有轮次盲于历史分数、其他轮次结果及目标刊会排名。不同审稿角色、提示词、模型或证据范围的结果可另作敏感性分析，不与同条件重复混算。分数碰巧相同可以是有效重复，但低方差不能证明调用独立或结论正确。

没有隔离上下文或真实独立调用能力时，报告可实际完成的单次判断，以及“未完成独立重复”。同一回复中多次自评、反思或列出五个数字不构成五个独立样本。部分执行失败时记录实际完成次数，补足真实调用或明确给出部分结果，不伪造缺失轮次。

**3．检查分歧，再按预先确定的规则追加**

五轮完成后，对同一对象、同一维度分别汇总。默认以下情况需要检查分歧，并在材料和事实不变的前提下再追加五轮，总计十轮：

- 任一已评分对象／维度的样本标准差达到 0.4 分。
- 创新性出现一级、二级、三级之间的分歧，或“经核实重复”与“存在新增贡献”的分歧。

次数和 0.4 阈值是本 skill 的工作约定，不是官方推荐或统计校准后的最佳参数。保留最初五轮，不能追加到得到满意分数为止，也不能删除不喜欢的有效轮次。用户明确指定较少次数时尊重其范围，报告分歧而不擅自扩充。

若分歧来自贡献遗漏、新文献、事实错误、核验范围不足或可靠性缺陷状态不一致，优先核查。证据或事实修正后更新 packet_id／protocol_id，另建批次，重新完成可比轮次；旧记录保留但不混算。材料不足不能靠重复调用解决，不能只删除未赋分轮次后宣布完整五轮完成。

十轮后仍分歧时，报告分数分布、各层级次数和具体争议，不继续无限追加。层级不能由均值四舍五入决定；若边界判据无法确定，就标明层级待定或层级分歧。已核实的核心反例、重要证据缺口或创新升级条件优先于多数票与均值。

**4．统计量与解释**

对同一对象、同一维度的实际有效点分 $x_1,\ldots,x_R$，计算算术均值及分母为 $R-1$ 的样本方差：

$$
\bar{x}=\frac{1}{R}\sum_{r=1}^{R}x_r,
\qquad
s^2=\frac{1}{R-1}\sum_{r=1}^{R}(x_r-\bar{x})^2.
$$

同时报告标准差 $s$、最小与最大分数、创新层级次数、可靠性缺陷状态次数、有效点分次数及实际独立执行次数。对核心与辅助创新点分别汇总，对每轮直接给出的整篇创新性另行汇总；不从创新点均值推导整篇分数，不计算四维总分。

点分与均值保留一位小数，样本方差保留三位，标准差保留两位。用未舍入的均值计算方差，并用未舍入的标准差检查追加条件。至少两个有效点分才计算样本方差和标准差；只有一次时它们是未定义状态，不能写成零。

暂无法判断、未核验及仅有区间的轮次不以零分或区间中点替代。若有部分有效点分，可计算其描述统计，但必须标明有效次数／实际次数、未赋分原因和“部分轮次未赋分”，不充当完整重复结论。

均值与方差描述模型在固定规则及证据下的判断波动。这套十分制是工作性评价量表，不是创新性真实价值的精确测量；不给未经校准的“真实创新性置信区间”或录用概率。低方差仍可能伴随共同误判，需以人工认可的边界案例与实际事实校准。

格式示例（虚构数字，仅示范计算）：6.2、6.4、6.3、6.5、6.4 的均值显示为 6.4，样本方差为 0.013，标准差为 0.11，范围为 6.2–6.5；这些点分均属于第二级。3.9 与 4.0 的均值虽可显示为 4.0，但存在二／三级分歧，不能据此直接判为第二级。

**5．记录格式与统计脚本**

在稿件工作目录保存 evidence-packet、assessment-batch.json、assessment-summary.json 和可选的 assessment-summary.md，不把真实稿件、评分记录或执行日志默认提交进 skill 仓库。保留逐轮成绩、依据与实际执行标识；脚本只计算统计，不发起模型调用，也无法证明输入中的调用真实发生。

assessment-batch.json 使用 schema_version=1。下面只示范一轮的字段，不代表真实评估或完整五轮。实际填写真实执行记录；当前成果与条件性潜力用 basis 区分：

~~~json
{
  "schema_version": 1,
  "batch_id": "format-example-not-a-real-evaluation",
  "packet_id": "frozen-evidence-version",
  "protocol_id": "fixed-rubric-model-and-task-version",
  "protocol": {
    "rubric_version": "actual-rule-version",
    "model_id": "actual-runtime-reported-model",
    "model_snapshot": null,
    "settings": {},
    "execution_method": "isolated_agents"
  },
  "planned_rounds": 5,
  "objects": [
    {
      "id": "c1",
      "label": "核心贡献",
      "kind": "contribution",
      "basis": "current",
      "dimensions": ["innovation"]
    },
    {
      "id": "overall",
      "label": "整篇工作",
      "kind": "overall",
      "basis": "current",
      "dimensions": ["innovation"]
    }
  ],
  "rounds": [
    {
      "round_id": "r1",
      "context_id": "actual-execution-context-or-request-id",
      "packet_id": "frozen-evidence-version",
      "protocol_id": "fixed-rubric-model-and-task-version",
      "scores": {
        "c1": {
          "innovation": {
            "status": "scored",
            "score": 6.2,
            "tier": 2,
            "rationale": "填写本轮与最邻近原始结果的具体差异和相邻锚点依据。"
          }
        },
        "overall": {
          "innovation": {
            "status": "scored",
            "score": 6.2,
            "tier": 2,
            "rationale": "填写核心贡献支撑主要结论的依据，不平均各贡献。"
          }
        }
      }
    }
  ]
}
~~~

对象 kind 为 contribution 时仅评价 innovation；每批恰有一个 overall 对象。完整审核在 overall.dimensions 中列出 innovation、importance、reliability、presentation。每轮必须显式覆盖所有对象及其声明维度，不能用缺少字段隐去未评分结果。

status 为 scored、undetermined 或 unverified。后两者 score 为 null，rationale 说明原因；只有区间判断时采用 undetermined，并在依据中保留区间。创新性点分须带正确的 tier；核实重复的 0.0 须使用 tier=null 与 duplicate_verified=true，其余三个维度不使用 0.0 或创新层级。

可靠性点分另带 verification_scope（已核查范围的文字）及 verification_state：core_refuted 对应 1.0–3.9，major_gap 对应 4.0–5.9，supported 对应 6.0–10.0。尚未核验不能填成 supported。脚本检查分数限制；核验真实性、充分性及 8.0 以上所需的针对性记录仍须实际审核。

protocol 记录真实可获知的模型与设置；无法获知快照时 model_snapshot=null，并说明可复现性的限制。API 调用可使用 independent_api_calls 作为 execution_method。每个实际新上下文／请求有独立 context_id；各轮 packet_id 与 protocol_id 必须一致。不同材料、设置、评价基础或历史批次不能为了增加样本数拼接。

~~~text
python "<skill-dir>/scripts/summarize_assessments.py" "<paper-dir>/assessment-batch.json" --output "<paper-dir>/assessment-summary.json" --markdown "<paper-dir>/assessment-summary.md"
~~~

脚本拒绝混用包或协议、重复执行标识、不完整的字段覆盖、无效或非有限分数、分数与创新层级不符，以及可靠性分数违反缺陷限制的记录。未知评分作为显式状态保留。输出后续动作建议，不自动追加模型调用；脚本与评分代理的职责分开。

同一稿件在新对话中评价时先加载固定材料与版本信息，新轮次仍不读取历史成绩；汇总时再比较历史批次。若用户允许直接复用已有完整批次，明确说本次复用了哪些真实轮次、没有新增调用，同一记录不能重复计为新的独立样本。

**6．官方依据与本 skill 的设计边界**

OpenAI 官方建议使用明确评分标准和参照案例，将判断组织为分类、比较或按具体条件评分，并通过人工反馈校准模型评估。这支持沿用整数锚点、先定级再打分和核查边界案例的做法。[Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)

官方提示工程指南建议固定模型快照并检查提示词表现；因此在条件允许时固定具体模型版本、规则和材料，并保存运行记录。skill 文字不能替运行环境设置无法控制的参数，也不能保证不同版本行为相同。[Prompt engineering](https://developers.openai.com/api/docs/guides/prompt-engineering)

参数支持须以实际模型和接口文档为准。本方案不依赖固定 seed；当前 Chat Completions 文档将该参数标记为弃用，且明确不保证确定性。不能通过反复回放相同的确定性输出来估计独立采样波动。[Chat Completions API reference](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create)

官方资料核对日期：2026-10-12。五轮、至多十轮、0.4 分阈值、字段格式和汇总精度是本 skill 针对稿件评价的设计，并非 OpenAI 给出的论文评分方法或统计保证。
