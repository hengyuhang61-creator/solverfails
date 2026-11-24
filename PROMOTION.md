# SolverFails launch material

## English project introduction

**For CFD and software reviewers: catch a false pass before you sign off.** Replay a Mach 5 SU2 checkpoint pair. First test the global mass budget and see it pass. Then check the wall feature and watch the result change to `HOLD_WALL_DRIFT`. The two separations are 7.20 mm apart even though both mass imbalances are below 0.004%.

The four cases also cover profile comparison support, a Fluent mass budget and installed-version verification. Each case includes the source boundary and a command that reproduces its disposition. The public Mach 5 case supplies the exact crossing coordinates, the threshold and the matching restart fingerprint.

[Replay the Mach 5 case](https://hengyuhang61-creator.github.io/solverfails/mach5-drift.html) · [Repository and CLI](https://github.com/hengyuhang61-creator/solverfails) · [Releases](https://github.com/hengyuhang61-creator/solverfails/releases/latest)

## 中文项目介绍

**给做 CFD 和软件验收的人：在签字前发现误判。** 重放两个 Mach 5 SU2 检查点。先单独核对质量预算，再加上壁面分离漂移检查。两份结果的质量误差均低于 0.004%，分离点却相差 7.20 mm。第二次核验给出 `HOLD_WALL_DRIFT`。

案例集还包括剖面样本覆盖、Fluent 边界质量预算及安装版本探测。每个案例都标明证据范围，并提供可重复运行的命令。Mach 5 案例公开分离与再附坐标、门槛以及连接两份状态的重启哈希。

[重放 Mach 5 案例](https://hengyuhang61-creator.github.io/solverfails/mach5-drift.html) · [源码和命令行](https://github.com/hengyuhang61-creator/solverfails) · [版本](https://github.com/hengyuhang61-creator/solverfails/releases/latest)

## Third-party community draft

**Draft.** Both Mach 5 checkpoints pass the global mass screen. The skin-friction zero still moves upstream by 7.20 mm. SolverFails lets you run each check on the same data and shows why the convergence decision changes. Which local quantity do you watch in addition to your global balance? [Try the replay](https://hengyuhang61-creator.github.io/solverfails/mach5-drift.html)
