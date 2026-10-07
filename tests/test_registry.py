"""Parameter registry: canonical spec registry, tags, explicit tunable flag, citation resolution, cap, sha."""

from pathlib import Path

import pytest

from fatpitch import registry as r

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "spec" / "registry.yaml"


def _p(i, tag="interpreted", value="1", rng="[0, 2]", tunable="true", citation="", extra=""):
    return (f"- id: p{i}\n  value: {value}\n  range: {rng}\n  tag: {tag}\n  citation: '{citation}'\n"
            f"  notes: ''\n  tunable: {tunable}\n{extra}")


def _y(*params) -> str:
    return "".join(params)


def test_canonical_registry_loads_with_citation_check():
    reg = r.load(SPEC, root=ROOT)
    assert reg.source_path == str(SPEC)
    assert len(reg.tunable) == 8
    assert all(p.tag == "interpreted" for p in reg.tunable)
    assert {p.tag for p in reg.parameters} == set(r.TAGS)
    # stated parameters may carry a descriptive range without being tunable
    sf = reg["size.starter_fraction"]
    assert sf.tag == "stated" and sf.range == (0.20, 0.33) and not sf.tunable
    assert reg["liq.m2_ip.spread_pp"].effective == 3.5
    assert r.load_default().sha256 == reg.sha256
    assert not r.DEFAULT_PATH.parent.joinpath("..", "registry", "parameters.example.yaml").exists()


def test_tunable_is_explicit_not_range():
    reg = r.loads(_y(_p(1, tunable="false"), _p(2, rng="null", tunable="false")))
    assert reg.tunable == []
    assert len(r.loads(_p(1)).tunable) == 1


def test_stated_requires_library_citation():
    with pytest.raises(r.RegistryError, match="requires a citation"):
        r.loads(_p(1, tag="stated", tunable="false"))
    with pytest.raises(r.RegistryError, match="requires a citation"):
        r.loads(_p(1, tag="stated", tunable="false", citation="Taylor (1993)"))
    assert r.loads(_p(1, tag="stated", tunable="false", citation="DS/2009-XX-XX_x.md (quote)"))


@pytest.mark.parametrize("tag", ["stated", "interpreted-from-article"])
def test_tunable_requires_interpreted(tag):
    with pytest.raises(r.RegistryError, match="must be tagged 'interpreted'"):
        r.loads(_p(1, tag=tag, citation="RS/2015-01-18_x.md"))


def test_tunable_cap_of_eight():
    assert len(r.loads(_y(*[_p(i) for i in range(8)])).tunable) == 8
    with pytest.raises(r.RegistryError, match="cap is 8"):
        r.loads(_y(*[_p(i) for i in range(9)]))
    assert len(r.loads(_y(*[_p(i) for i in range(8)], _p(99, tunable="false"))).tunable) == 8


@pytest.mark.parametrize("text,msg", [
    (_p(1, tag="guessed"), "tag"),
    (_y(_p(1), _p(1)), "duplicate"),
    (_p(1, rng="null"), "numeric range"),
    (_p(1, rng="[2, 1]"), "low"),
    (_p(1, value="5"), "outside range"),
    (_p(1, tunable="maybe"), "tunable must be"),
    ("- id: p1\n  value: 1\n  tag: interpreted\n", "missing required"),
    (_p(1, extra="  colour: red\n"), "unknown keys"),
])
def test_validation_errors(text, msg):
    with pytest.raises(r.RegistryError, match=msg):
        r.loads(text)


def test_citation_resolution(tmp_path):
    ds = tmp_path / "library" / "discovered_sources"
    ds.mkdir(parents=True)
    (ds / "2009-XX-XX_citi-fxlm-fireside-jeff-feig.md").write_text("x", encoding="utf-8")
    ok = [_p(1, tag="stated", tunable="false", citation="DS/2009-XX-XX_citi-fxlm-fireside-jeff-feig.md (q)"),
          _p(2, tag="stated", tunable="false", citation="DS/2009-XX-XX_citi-fxlm"),       # partial with date prefix
          _p(3, tag="interpreted", tunable="false", citation="none (design choice)")]
    assert len(r.loads(_y(*ok), root=tmp_path)) == 3
    bad = _p(4, tag="stated", tunable="false", citation="RS/2015-01-18_lost-tree-club-speech.md")
    assert r.loads(bad)                                       # no root: not checked
    with pytest.raises(r.RegistryError, match="not found"):
        r.loads(bad, root=tmp_path)
    with pytest.raises(r.RegistryError, match="not found"):
        r.loads(_p(5, tag="stated", tunable="false", citation="DS/2010-01-01_missing"), root=tmp_path)


def test_mapping_layout_accepted():
    text = "registry_version: 2\nparameters:\n" + "\n".join("  " + ln for ln in _p(1).splitlines())
    reg = r.loads(text)
    assert reg.version == 2 and len(reg) == 1


def test_sha_ignores_formatting_tracks_content():
    a = r.loads(_y(_p(1), _p(2, tunable="false", value="3")))
    b = r.loads("# comment\n" + _y(_p(1), _p(2, tunable="false", value="3")).replace("value: 3", "value:    3"))
    c = r.loads(_y(_p(1), _p(2, tunable="false", value="4")))
    assert a.sha256 == b.sha256 != c.sha256
    assert len(a.sha256) == 64
    assert r.empty().sha256 == r.loads("[]").sha256 == r.loads("parameters: []").sha256
