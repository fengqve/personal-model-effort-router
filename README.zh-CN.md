# FitMyTask

**用自己的任务验收证据，选择模型与推理档位。**

[English](README.md) · [数据格式](docs/evidence.md) · [接入 Agent](docs/integration.md) · [方法与局限](docs/method.md)

新模型发布、开始新项目、任务变难、质量下降、成本上升或工作流变化，都可能让原来的模型选择不再合适。

FitMyTask 是一个在本地运行的 Python 小工具：读取完整任务的评测记录，为下一个任务选择模型与推理档位，并解释依据。保留已有评测器和执行工具，通过显式适配器接入自动调用。

**当前为 v0.1.0 实验版。演示使用虚构模型和合成数据，没有真实模型优势、节省比例或分类准确率结论。**

## 30 秒试用

需要 Python 3.9+；没有运行时依赖，不需要 API Key、联网或安装。从仓库根目录运行：

```sh
python3 -m fitmytask demo
python3 -m unittest discover -s tests -v
```

也可从源码安装：`python3 -m pip install .`，随后使用 `fitmytask demo`。目前没有发布 PyPI 包。

演示比较六个共同样本：虚构的小模型低档通过 4/6、平均任务成本 $0.02；小模型高档通过 6/6、$0.08；大模型高档通过 6/6、$0.30。程序选择小模型高档，因为它在这组合成数据中满足验收门槛且成本更低。**这些数字不是任何真实模型的性能结论，模拟结果不能用于 dispatch。**

## 接入真实任务

1. 固定代表性任务、输入与验收标准，用已有评测器运行模型与档位组合。
2. 按[数据格式](docs/evidence.md)记录完整任务，包括失败、重试、协调和返工；未知金额写 `null`。
3. 由宿主 Agent 给新任务标注已知任务类别、风险、执行环境版本和验收标准；分类不确定时写 `classification_confirmed: false`。
4. 生成可审阅的选择：

```sh
python3 -m fitmytask route   --catalog private/catalog.json   --runs private/runs.jsonl   --task private/task.json
```

输出包含模型和档位、独立样本数、经验通过率、完整任务成本与耗时、不合格原因及局限。高风险或分类未确认时返回 `review_required`，不自动选择。

需要执行时，通过 `dispatch` 将选择和任务交给显式指定的本地程序，并保存其结果记录。详见[接入协议](docs/integration.md)。适配器不是沙箱，可能按其自身权限产生费用或修改文件；工具核心不直接调用提供商，也不修改全局 Agent 配置。

## 首版范围

已实现模型与档位联合选择、相同任务集合比较、失败成本保留、重复样本去重、过期/合成证据隔离、门槛检查、选择解释，以及适配器调用和结果记录。

尚未内置语义分类器、模型提供商适配器、Promptfoo/LiteLLM 原生导入、评测执行器、实时价目表或自动升级重试。分类由宿主 Agent 提供，完成判断由评测器负责，模型和档位由适配器实际应用。**历史平均成本上限不是本次调用的硬预算上限**；超时也不保证远程请求或所有子进程已终止。

## 与已有工具的关系

[RouteLLM](https://github.com/lm-sys/RouteLLM)、[LiteLLM](https://docs.litellm.ai/docs/proxy/auto_routing) 已有评测或自动路由能力，[Promptfoo](https://www.promptfoo.dev/docs/configuration/expected-outputs/) 提供输出评测，[OpenAI](https://developers.openai.com/api/docs/guides/model-selection) 已有模型与推理档位的选型指导。

我们探索的是更小的一环：让你自己的任务验收记录直接参与下一次模型和档位选择，并把依据保留下来。不声称首次发明评测、路由，也不声称官方完全没有相关能力。

欢迎贡献可复现任务、验收标准、适配器、分类错误分析和失败结果。提交前移除私有资料和凭证。采用 MIT 许可证；使用 AI 协助开发，维护者负责审阅。
