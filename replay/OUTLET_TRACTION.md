# The outlet mass flow agrees while the transverse update fails

Two native SU2 8.6.0 cases have the same grid, initial field and runtime settings. The ordinary pressure outlet and dedicated supersonic outlet each give 11.2 kg/s per metre span within a relative tolerance of $10^{-6}$. An acceptance rule based on outlet mass flow alone accepts both.

The independent check is the transverse momentum balance. With $\mu=0.001$ Pa·s and $du/dy=2{,}000$ s⁻¹, the streamwise outlet face carries 2 Pa of transverse traction. Over the first explicit step the opposing face balances this contribution, giving zero local transverse momentum density rate in the central strip. Omitting the outlet term in the 1 mm-wide boundary control volume gives −2,000 kg/(m² s²). The pressure-marker output reproduces this failure while the dedicated-marker output and zero-shear control satisfy the bound. This checks a local equation term in a manufactured state. Applying the bound to a different flow requires that flow's own balance and tolerance.

```sh
python replay/outlet_traction_witness.py
```

Python 3.9+ suffices. The adjacent CSV contains the 17 outlet nodes per case and their original momentum values from the SU2 8.6.0 coarse dedicated, ordinary and uniform runs. The script integrates all 17 nodes for mass flow, checks the central nine for the transverse update, and returns a nonzero exit code if the witness changes. The correct acceptance rule in this case requires the outlet mass test **and** the local balance with a tolerance of 20 kg/(m² s²). It leaves other equations and general convergence unassessed.

The original mesh, restart, output, hashes and source comparison can be recovered from the MachAtlas release. This regression uses one upstream mechanism. Its two passing controls and refined-grid study counts do not add independent mechanisms. [MachAtlas native archive](https://github.com/hengyuhang61-creator/machatlas/releases/tag/v0.3.2) · [Upstream change](https://github.com/su2code/SU2/pull/2829)
