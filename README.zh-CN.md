# SolverFails

本地打开 [网格外推与问卷分母案例](site/witnesses.html)，或在仓库根目录运行 `python replay/witness.py`（Python 3.9 及以上，标准库）。上游 Poiseuille 测试通过，外推误差却达到 0.00454193；两份真实模型回放引用了正确的问卷，却将 18% 的受访者写成了患者。

运行 `python replay/witness.py summary` 查看原判据与新判据的错误接受、错误拒绝和弃判，`python replay/witness.py json` 导出逐条证据。页面同时保留了新判据也会误收的积分反例。可通过[投稿说明](CONTRIBUTING.md)提交一个公开链接、命令或标签纠错，并选择署名。

**给做 CFD 和软件验收的人：重放一次由通过信号掩盖的真实失败。**

[打开交互案例集](https://hengyuhang61-creator.github.io/solverfails/) · [版本发布](https://github.com/hengyuhang61-creator/solverfails/releases/latest) · [反馈](https://github.com/hengyuhang61-creator/solverfails/issues/new)

- 剖面末端钳制让 RMSE 变成 0，计算剖面仅覆盖 21 个参考点中的 13 个。可在浏览器切换评分方式和样本数。
- Fluent 真实检查点的连续性缩放残差低于 0.001，完整边界的质量不平衡仍为 1.0408%。可根据标量摘录重新计账。
- Personal OS 的历史交付记录显示候选构建成功，安装入口仍是旧版本。公开演示用合成版本号重现交付验收错误。

本地运行指令见[英文 README](README.md)。来源、脱敏边界和许可见[说明](THIRD_PARTY_NOTICES.md)。

从 [Mach 5 原生案例](https://hengyuhang61-creator.github.io/solverfails/mach5-drift.html)。先点击质量检查，再加入壁面检查。两个检查点的质量误差均低于 0.004%，分离位置仍移动 7.20 mm。
