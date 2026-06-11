from ui.responsive_styles import MOBILE_BREAKPOINT_PX, NARROW_BREAKPOINT_PX, RESPONSIVE_CSS


def test_responsive_css_includes_mobile_breakpoints():
    assert f"@media (max-width: {MOBILE_BREAKPOINT_PX}px)" in RESPONSIVE_CSS
    assert f"@media (max-width: {NARROW_BREAKPOINT_PX}px)" in RESPONSIVE_CSS


def test_responsive_css_stacks_columns_on_mobile():
    assert 'div[data-testid="column"]' in RESPONSIVE_CSS
    assert "flex: 1 1 100%" in RESPONSIVE_CSS


def test_responsive_css_full_width_buttons_on_mobile():
    assert 'div[data-testid="stButton"] button' in RESPONSIVE_CSS
    assert "width: 100%" in RESPONSIVE_CSS
