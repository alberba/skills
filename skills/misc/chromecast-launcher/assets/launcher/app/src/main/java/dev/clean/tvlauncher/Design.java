package dev.clean.tvlauncher;

import java.util.ArrayList;
import java.util.List;

/** One selectable look for the launcher. All sizes are dp. Add a design by appending to ALL. */
final class Design {
    /** hero: 0 none, 1 text left + art right, 2 centred text, 3 big text left, 4 art left + text right. */
    String name;
    int bg = 0xff050507, fg = 0xffffffff, fg2 = 0xb3ffffff, tileBg = 0xff1d1d24, tint = 0;
    int pillBg = 0x26ffffff, pillFg = 0xffffffff, pillFocusBg = 0xf2ffffff, pillFocusFg = 0xff101014, pillRadius = 30;
    int stroke = 0x55ffffff, strokeW = 0;
    float ambient = 1f, scale = 1.10f;
    /** 0 top wash + corner glow, 1 centre glow, 2 bottom glow, 3 none. */
    int ambientMode = 0;
    int hero = 1, heroW = 252, heroH = 142, heroRadius = 18, titleSize = 42, titleWeight = 600, clockSize = 24, clockWeight = 300;
    boolean grid, labelsAlways, fit, mono, upper, date = true;
    String body = "Outfit.ttf", display = "Outfit.ttf";
    float tracking = 0f;
    int favW = 162, favH = 91, appW = 162, appH = 91, gap = 12, radius = 12;

    private Design(String name) { this.name = name; }

    static final List<Design> ALL = new ArrayList<>();

    static {
        Design d = new Design("Taller");
        d.bg = 0xff1b1a18; d.fg = 0xffe6e1d7; d.fg2 = 0xff9b958a; d.tileBg = 0xff232220; d.tint = 0xffe8703f;
        d.ambient = 0.55f; d.ambientMode = 2; d.radius = 22; d.heroRadius = 22; d.scale = 1.1f; d.hero = 1;
        d.stroke = 0xffe8703f; d.strokeW = 2; d.titleSize = 28; d.clockSize = 18; d.tracking = -0.04f;
        d.body = "Manrope.ttf"; d.display = "Unbounded.ttf"; d.titleWeight = 600; d.clockWeight = 500;
        d.pillBg = 0xff2c2b28; d.pillFg = 0xffc4beb3; d.pillFocusBg = 0xffe8703f; d.pillFocusFg = 0xff1b1a18;
        ALL.add(d);

        d = new Design("Apple TV");
        ALL.add(d);

        d = new Design("Apple claro");
        d.bg = 0xfff2f2f7; d.fg = 0xff111114; d.fg2 = 0x99111114; d.tileBg = 0xffe0e0e8;
        d.pillBg = 0x14000000; d.pillFg = 0xff111114; d.pillFocusBg = 0xff111114; d.pillFocusFg = 0xffffffff;
        d.stroke = 0x33000000; d.ambient = 0.45f; d.radius = 16; d.heroRadius = 22;
        ALL.add(d);

        d = new Design("Cine");
        d.hero = 3; d.titleSize = 58; d.titleWeight = 700; d.favW = 130; d.favH = 73; d.appW = 130; d.appH = 73;
        d.gap = 20; d.radius = 6; d.scale = 1.2f; d.ambient = 1.5f; d.stroke = 0; d.strokeW = 0;
        ALL.add(d);

        d = new Design("Centro");
        d.hero = 2; d.titleSize = 44; d.ambientMode = 1; d.ambient = 1.3f; d.radius = 14;
        ALL.add(d);

        d = new Design("Mosaico");
        d.hero = 0; d.grid = true; d.labelsAlways = true; d.favW = 120; d.favH = 68; d.appW = 120; d.appH = 68;
        d.gap = 16; d.scale = 1.1f; d.clockSize = 30; d.ambient = 0.6f; d.radius = 10;
        ALL.add(d);

        d = new Design("Dock");
        d.hero = 0; d.favW = 200; d.favH = 112; d.appW = 96; d.appH = 54; d.gap = 16; d.radius = 16;
        d.ambientMode = 2; d.ambient = 0.9f; d.clockSize = 48; d.scale = 1.1f;
        ALL.add(d);

        d = new Design("Minimal");
        d.hero = 0; d.ambientMode = 3; d.clockSize = 64; d.clockWeight = 200; d.radius = 14; d.gap = 18;
        d.stroke = 0x33ffffff; d.scale = 1.1f;
        ALL.add(d);

        d = new Design("Cálido");
        d.bg = 0xff130d08; d.fg = 0xfff5e6d3; d.fg2 = 0xaaf5e6d3; d.tileBg = 0xff2a1d12; d.tint = 0xffb5651d;
        d.ambientMode = 2; d.ambient = 1.4f; d.radius = 10; d.hero = 4; d.heroRadius = 10;
        d.pillBg = 0x33f5e6d3; d.pillFg = 0xfff5e6d3; d.pillFocusBg = 0xfff5e6d3; d.pillFocusFg = 0xff130d08;
        d.stroke = 0x66f5e6d3;
        ALL.add(d);

        d = new Design("Neón");
        d.bg = 0xff06050d; d.fg = 0xffffffff; d.fg2 = 0xff7fdcff; d.tileBg = 0xff101020; d.tint = 0xff3b0fd6;
        d.ambientMode = 1; d.ambient = 1.2f; d.radius = 4; d.heroRadius = 4; d.upper = true; d.scale = 1.1f;
        d.stroke = 0xff00e5ff; d.strokeW = 2; d.titleWeight = 700;
        d.pillBg = 0x2200e5ff; d.pillFg = 0xff7fdcff; d.pillFocusBg = 0xff00e5ff; d.pillFocusFg = 0xff06050d; d.pillRadius = 6;
        ALL.add(d);

        d = new Design("Cristal");
        d.hero = 4; d.radius = 26; d.heroRadius = 30; d.fit = true; d.tileBg = 0x30ffffff;
        d.ambientMode = 1; d.ambient = 1.6f; d.scale = 1.1f; d.stroke = 0x88ffffff;
        d.pillBg = 0x33ffffff; d.pillFocusBg = 0xccffffff;
        ALL.add(d);

        d = new Design("Retro");
        d.bg = 0xff020a03; d.fg = 0xff39ff6a; d.fg2 = 0xff1fa346; d.tileBg = 0xff0a1a0c; d.mono = true; d.upper = true;
        d.hero = 3; d.titleSize = 34; d.ambientMode = 3; d.radius = 0; d.heroRadius = 0; d.fit = true; d.scale = 1.10f;
        d.stroke = 0xff39ff6a; d.strokeW = 2;
        d.pillBg = 0x1a39ff6a; d.pillFg = 0xff39ff6a; d.pillFocusBg = 0xff39ff6a; d.pillFocusFg = 0xff020a03; d.pillRadius = 0;
        ALL.add(d);

        d = new Design("Iconos");
        d.fit = true; d.labelsAlways = true; d.favW = 100; d.favH = 100; d.appW = 100; d.appH = 100; d.gap = 20;
        d.radius = 24; d.heroW = 142; d.heroH = 142; d.heroRadius = 30; d.scale = 1.12f;
        ALL.add(d);
    }
}
