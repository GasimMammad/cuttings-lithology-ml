# v5: expert-panel adjudication of the 40 spot-check bins (34/7-10). Plan written before any panel output.

## Why

- Two AI core raters (A Opus, B Sonnet) disagreed directionally in 34/7-10:
  51 bins where A said SAND and B said HET/MUD.
- The author could not adjudicate from photographs alone. Instead of more AI
  opinions, the panel weighs INDEPENDENT EVIDENCE:
  1. the operator's own core description (well and core reports on T9,
     written by a human sedimentologist with the core in hand);
  2. wireline logs at the core depths (density, neutron, sonic, resistivity,
     GR), with an estimated core-to-log depth shift;
  3. core plugs (34_7-10_CORE_CONV_RAW_1.SPWLA, report PDFs): porosity,
     permeability, grain density;
  4. cuttings XRF at the same depths (bag scale, about 3 m);
  5. published literature on the Statfjord Gp (basal Amundsen, Nansen,
     Eiriksson, Raude) in the Tampen Spur / Snorre-Visund area;
  6. the core photographs themselves.

## Who

All are AI agents (Claude). This is NOT a human expert panel.
- **Agent 1:** senior petrophysicist / core analyst persona. Logs, plugs,
  core reports, photos, literature.
- **Agent 2:** senior geochemist persona. Cuttings XRF, chemostratigraphy,
  representativeness of coring cuttings, literature.
- **Agent 3:** the existing reviewer (general geoscientist + ML). Challenges
  everything.

## Blinding

- Agents 1 and 2 get the 40 bins WITHOUT the raters' labels
  (`v5_panel/items_blind.csv`).
- The answer key (`results/v4/spotcheck_key.csv`) is revealed only after the
  panel has fixed its per-bin consensus.

## Procedure

- **R1:** agents 1 and 2 work independently. Per bin: lithology (SAND / HET /
  MUD / OTHER / NO-CORE / UNRESOLVED), confidence, and the evidence used.
- **R2:** agent 3 critiques both. Agents 1 and 2 answer and revise. Repeat
  until positions stop changing, at most 3 rounds.
- **Consensus label per bin:**
  - agreed by agents 1 and 2 with at least one non-photographic evidence
    line (operator core description, logs, plugs) supporting it;
  - otherwise UNRESOLVED.
  - "100% correct" is not claimed. Unresolved bins are reported as such.
- **Then reveal the key:** rate at which A's and B's disputed calls match the
  consensus, with Wilson CIs, and a statement of which rater is biased, if
  the evidence supports one.
