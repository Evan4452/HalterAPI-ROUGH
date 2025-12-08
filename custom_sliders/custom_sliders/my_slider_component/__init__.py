import os
import streamlit.components.v1 as components

# Get absolute path to frontend folder
_parent_dir = os.path.dirname(os.path.abspath(__file__))
_build_dir = os.path.join(_parent_dir, "frontend")

# Declare component
_my_slider = components.declare_component(
    "my_slider",
    path=_build_dir
)

def my_slider_component(
    total_bullish: int,
    total_bearish: int,
    default_bullish: int,
    default_bearish: int,
    key=None
):
    """
    Renders custom slider component and returns (bullish_val, bearish_val)
    """
    result = _my_slider(
        total_bullish=total_bullish,
        total_bearish=total_bearish,
        default_bullish=default_bullish,
        default_bearish=default_bearish,
        key=key,
        default=(default_bullish, default_bearish)
    )
    if result is None:
        return default_bullish, default_bearish
    return tuple(map(int, result))
