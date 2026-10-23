package dev.clean.tvlauncher;

import android.animation.ArgbEvaluator;
import android.animation.ValueAnimator;
import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;
import android.content.pm.ResolveInfo;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.LinearGradient;
import android.graphics.Outline;
import android.graphics.Paint;
import android.graphics.RadialGradient;
import android.graphics.Shader;
import android.graphics.Typeface;
import android.graphics.drawable.Drawable;
import android.graphics.drawable.GradientDrawable;
import android.net.wifi.WifiManager;
import android.os.Bundle;
import android.os.Handler;
import android.provider.Settings;
import android.view.Gravity;
import android.view.KeyEvent;
import android.view.View;
import android.view.ViewGroup;
import android.view.ViewOutlineProvider;
import android.view.animation.DecelerateInterpolator;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import java.text.DateFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.Date;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;

public final class MainActivity extends Activity {
    private static final int SIDE = 48;
    private Design design = Design.ALL.get(0);
    private int lastColor = 0xff3a3a5c;
    private TextView bgButton;
    private static final int FAV_MAX = 5;
    private AppEntry moving;
    private boolean staged;
    private boolean focusWatcherSet;
    private float stageP, stageQ, targetP, targetQ;
    private int stageGridB, stageGridC, stageHeightDp, stageFavOut;
    private int stageYa, stageDelta, stageHide, stageCopyShift;
    private FrameLayout favBox, heroArtHolder;
    private LinearLayout heroCopy;
    private GradientDrawable favPanel;
    private ValueAnimator stageAnim;
    private int bgMode;
    private static final String[] BG_NAMES = { "Clásico", "Aurora", "Malla", "Artwork", "Montañas", "Hora del día", "Geométrico", "Taller", "Espacio" };
    private final Handler handler = new Handler();
    private final List<AppEntry> dockApps = new ArrayList<>();
    private final List<AppEntry> otherApps = new ArrayList<>();
    private RecyclerView dockList;
    private RecyclerView gridList;
    private TextView clockText;
    private TextView dateText;
    private TextView heroEyebrow;
    private TextView heroTitle;
    private TextView heroHint;
    private ImageView heroArt;
    private TextView wifiButton;
    private TextView settingsButton;
    private AmbientView ambient;
    private ValueAnimator ambientAnim;
    private FrameLayout screenRoot;
    private boolean restoringFocus;
    private Typeface clockFace;
    private Typeface regular;
    private Typeface medium;
    private Typeface titleFace;

    private final Runnable tick = new Runnable() {
        @Override public void run() {
            Date now = new Date();
            clockText.setText(DateFormat.getTimeInstance(DateFormat.SHORT, Locale.getDefault()).format(now));
            dateText.setText(DateFormat.getDateInstance(DateFormat.FULL, Locale.getDefault()).format(now));
            handler.postDelayed(this, 30_000L);
        }
    };

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().getDecorView().setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_FULLSCREEN | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
            View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY | View.SYSTEM_UI_FLAG_LAYOUT_STABLE);
        design = Design.ALL.get(1);
        bgMode = getPreferences(MODE_PRIVATE).getInt("bg", 4) % BG_NAMES.length;
        loadApps();
        buildScreen();
        handler.post(tick);
    }

    @Override protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        int forced = intent.getIntExtra("design", -1);
        int forcedBg = intent.getIntExtra("bg", -1);
        if (forcedBg >= 0 && forcedBg < BG_NAMES.length) {
            bgMode = forcedBg;
            getPreferences(MODE_PRIVATE).edit().putInt("bg", forcedBg).apply();
            if (forced < 0) forced = Design.ALL.indexOf(design);
        }
        if (forced >= 0 && forced < Design.ALL.size()) {
            buildScreen();
            handler.removeCallbacks(tick);
            handler.post(tick);
            restoringFocus = false;
            restoreFocus();
        }
    }

    @Override protected void onResume() {
        super.onResume();
        if (dockList != null) dockList.post(new Runnable() { @Override public void run() { restoreFocus(); } });
    }

    @Override protected void onDestroy() {
        handler.removeCallbacks(tick);
        if (ambientAnim != null) ambientAnim.cancel();
        super.onDestroy();
    }

    private Typeface font(String asset, int weight) {
        if (design.mono) return Typeface.create(Typeface.MONOSPACE, weight >= 500 ? Typeface.BOLD : Typeface.NORMAL);
        try {
            Typeface face = new Typeface.Builder(getAssets(), asset).setFontVariationSettings("'wght' " + weight).build();
            if (face != null) return face;
        } catch (RuntimeException ignored) {}
        return Typeface.create("sans-serif", Typeface.NORMAL);
    }

    private void cycleBackground() {
        bgMode = (bgMode + 1) % BG_NAMES.length;
        getPreferences(MODE_PRIVATE).edit().putInt("bg", bgMode).apply();
        buildScreen();
        handler.removeCallbacks(tick);
        handler.post(tick);
        bgButton.post(new Runnable() { @Override public void run() { bgButton.requestFocus(); } });
    }


    private void loadApps() {
        PackageManager pm = getPackageManager();
        Set<String> seen = new HashSet<>();
        for (int i = 0; i < LauncherConfig.DOCK_PACKAGES.length; i++) {
            String packageName = LauncherConfig.DOCK_PACKAGES[i];
            AppEntry entry = resolvePackage(pm, packageName, LauncherConfig.DOCK_FALLBACK_LABELS[i]);
            dockApps.add(entry);
            seen.add(packageName);
        }
        collect(pm, intentFor(Intent.CATEGORY_LEANBACK_LAUNCHER), seen);
        collect(pm, intentFor(Intent.CATEGORY_LAUNCHER), seen);
        Collections.sort(otherApps, byLabel());
        applySavedOrder();
    }

    private Comparator<AppEntry> byLabel() {
        return new Comparator<AppEntry>() { @Override public int compare(AppEntry a, AppEntry b) { return a.label.toString().toLowerCase(Locale.ROOT).compareTo(b.label.toString().toLowerCase(Locale.ROOT)); } };
    }

    /** Restores the favourites and app order the user arranged with the move mode. */
    private void applySavedOrder() {
        String savedFavs = getPreferences(MODE_PRIVATE).getString("favs", null);
        if (savedFavs == null) return;
        java.util.Map<String, AppEntry> pool = new java.util.LinkedHashMap<>();
        for (AppEntry e : dockApps) pool.put(e.packageName, e);
        for (AppEntry e : otherApps) pool.put(e.packageName, e);
        dockApps.clear();
        otherApps.clear();
        for (String pkg : savedFavs.split(",")) {
            AppEntry e = pool.remove(pkg);
            if (e != null && dockApps.size() < FAV_MAX) dockApps.add(e);
        }
        for (String pkg : getPreferences(MODE_PRIVATE).getString("apps", "").split(",")) {
            AppEntry e = pool.remove(pkg);
            if (e != null && e.installed) otherApps.add(e);
        }
        List<AppEntry> fresh = new ArrayList<>();
        for (AppEntry e : pool.values()) if (e.installed) fresh.add(e);
        Collections.sort(fresh, byLabel());
        otherApps.addAll(fresh);
        if (dockApps.isEmpty() && !otherApps.isEmpty()) dockApps.add(otherApps.remove(0));
    }

    private void saveOrder() {
        StringBuilder favs = new StringBuilder(), apps = new StringBuilder();
        for (AppEntry e : dockApps) favs.append(favs.length() > 0 ? "," : "").append(e.packageName);
        for (AppEntry e : otherApps) apps.append(apps.length() > 0 ? "," : "").append(e.packageName);
        getPreferences(MODE_PRIVATE).edit().putString("favs", favs.toString()).putString("apps", apps.toString()).apply();
    }

    private Intent intentFor(String category) {
        return new Intent(Intent.ACTION_MAIN).addCategory(category);
    }

    private void collect(PackageManager pm, Intent query, Set<String> seen) {
        List<ResolveInfo> matches = pm.queryIntentActivities(query, 0);
        for (ResolveInfo info : matches) {
            String pkg = info.activityInfo.packageName;
            if (pkg.equals(getPackageName()) || !info.activityInfo.enabled || !info.activityInfo.applicationInfo.enabled || !seen.add(pkg)) continue;
            CharSequence label = info.loadLabel(pm);
            Drawable icon = info.loadIcon(pm);
            Drawable banner = null;
            try { banner = info.activityInfo.loadBanner(pm); } catch (RuntimeException ignored) {}
            otherApps.add(new AppEntry(pkg, label == null ? pkg : label, icon, banner, true));
        }
    }

    private AppEntry resolvePackage(PackageManager pm, String packageName, String fallback) {
        try {
            ApplicationInfo info = pm.getApplicationInfo(packageName, 0);
            if (!info.enabled) return new AppEntry(packageName, fallback, null, null, false);
            CharSequence label = pm.getApplicationLabel(info);
            Drawable icon = pm.getApplicationIcon(info);
            Drawable banner = null;
            try { banner = pm.getApplicationBanner(info); } catch (RuntimeException ignored) {}
            return new AppEntry(packageName, label == null ? fallback : label, icon, banner, true);
        } catch (PackageManager.NameNotFoundException absent) {
            return new AppEntry(packageName, fallback, null, null, false);
        }
    }

    private void buildScreen() {
        Design d = design;
        clockFace = font(d.display, d.clockWeight);
        regular = font(d.body, 400);
        medium = font(d.body, 600);
        titleFace = font(d.display, d.titleWeight);
        getWindow().setStatusBarColor(d.bg);
        getWindow().setNavigationBarColor(d.bg);
        getWindow().getDecorView().setBackgroundColor(d.bg);
        heroEyebrow = null; heroTitle = null; heroHint = null; heroArt = null; heroArtHolder = null; heroCopy = null;
        if (stageAnim != null) stageAnim.cancel();
        stageP = 0f; stageQ = 0f; targetP = 0f; targetQ = 0f;
        screenRoot = new FrameLayout(this);
        screenRoot.setBackgroundColor(d.bg);
        ambient = new AmbientView();
        ambient.color = lastColor;
        screenRoot.addView(ambient, new FrameLayout.LayoutParams(-1, -1));
        LinearLayout page = new LinearLayout(this);
        page.setOrientation(LinearLayout.VERTICAL);
        page.setClipChildren(false);
        page.setClipToPadding(false);
        page.setPadding(0, dp(10), 0, dp(6));
        screenRoot.addView(page, new FrameLayout.LayoutParams(-1, -1));
        setContentView(screenRoot);

        LinearLayout top = new LinearLayout(this);
        top.setGravity(Gravity.CENTER_VERTICAL);
        top.setOrientation(LinearLayout.HORIZONTAL);
        top.setPadding(dp(SIDE), 0, dp(SIDE), 0);
        top.setClipChildren(false);
        top.setClipToPadding(false);
        page.addView(top, new LinearLayout.LayoutParams(-1, dp(Math.max(52, d.clockSize + 24))));
        clockText = text("", d.clockSize, d.fg, clockFace);
        clockText.setLetterSpacing(d.tracking);
        top.addView(clockText);
        dateText = text("", 12, d.fg2, regular);
        LinearLayout.LayoutParams dateLp = new LinearLayout.LayoutParams(-2, -2);
        dateLp.leftMargin = dp(14);
        dateLp.topMargin = dp(5);
        dateText.setVisibility(d.date ? View.VISIBLE : View.GONE);
        top.addView(dateText, dateLp);
        top.addView(new View(this), new LinearLayout.LayoutParams(0, 1, 1));
        top.addView(new View(this), new LinearLayout.LayoutParams(dp(8), 1));
        bgButton = (TextView) pill("Fondo · " + BG_NAMES[bgMode], "Cambiar de fondo", new View.OnClickListener() {
            @Override public void onClick(View v) { cycleBackground(); }
        });
        top.addView(bgButton, wrap());
        top.addView(new View(this), new LinearLayout.LayoutParams(dp(8), 1));
        wifiButton = (TextView) pill(wifiLabel(), "Abrir ajustes de Wi-Fi", systemAction(Settings.ACTION_WIFI_SETTINGS, "Ajustes no disponibles"));
        top.addView(wifiButton, wrap());
        top.addView(new View(this), new LinearLayout.LayoutParams(dp(8), 1));
        settingsButton = (TextView) pill("Ajustes", "Abrir ajustes del sistema", systemAction(Settings.ACTION_SETTINGS, "Ajustes no disponibles"));
        top.addView(settingsButton, wrap());

        staged = !d.grid;
        if (staged) {
            buildStage(page, Math.max(52, d.clockSize + 24) + 16);
        } else {
            page.addView(new View(this), new LinearLayout.LayoutParams(1, 0, 0.0001f));
            dockList = addRow(page, "Favoritas", dockApps, true, d.favW, d.favH, true);
            gridList = addRow(page, "Aplicaciones", otherApps, false, d.appW, d.appH, true);
        }
        if (!focusWatcherSet) {
            focusWatcherSet = true;
            getWindow().getDecorView().getViewTreeObserver().addOnGlobalFocusChangeListener(new android.view.ViewTreeObserver.OnGlobalFocusChangeListener() {
                @Override public void onGlobalFocusChanged(View oldFocus, View newFocus) {
                    if (!staged || newFocus == null || gridList == null) return;
                    if (!isInside(newFocus, gridList)) { setStageTarget(0f, 0f); return; }
                    View cell = newFocus;
                    while (cell.getParent() != gridList && cell.getParent() instanceof View) cell = (View) cell.getParent();
                    int pos = gridList.getChildAdapterPosition(cell);
                    int cols = ((androidx.recyclerview.widget.GridLayoutManager) gridList.getLayoutManager()).getSpanCount();
                    setStageTarget(1f, pos >= 3 * cols ? 1f : 0f);
                }
            });
        }
    }

    private boolean isInside(View view, View ancestor) {
        for (android.view.ViewParent p = view.getParent(); p != null; p = p.getParent()) if (p == ancestor) return true;
        return false;
    }

    /**
     * Apple TV style home. Favourites sit in a translucent panel at the bottom with the hero above (p = 0);
     * moving down dissolves the panel and the favourites become the first row above the apps (p = 1).
     */
    private void buildStage(LinearLayout page, int chromeDp) {
        Design d = design;
        android.util.DisplayMetrics dm = getResources().getDisplayMetrics();
        int stageH = (int) (dm.heightPixels / dm.density) - chromeDp;
        int rowH = d.favH + 32;
        stageYa = stageH - rowH - 6;
        int yB = d.hero == 0 ? 40 : 10;
        stageDelta = stageYa - yB;
        stageHide = stageDelta + rowH + 10;
        stageHeightDp = stageH;
        stageGridB = yB + rowH - 6;
        stageGridC = 6;
        stageFavOut = yB + rowH + 24;
        stageCopyShift = (stageYa - 4) - (yB - 10);
        FrameLayout stage = new FrameLayout(this);
        stage.setClipChildren(false);
        stage.setClipToPadding(false);
        page.addView(stage, new LinearLayout.LayoutParams(-1, 0, 1));
        if (d.hero != 0) buildHero(stage, new FrameLayout.LayoutParams(-1, dp(stageYa - 4)));

        favBox = new FrameLayout(this);
        favBox.setClipChildren(false);
        favBox.setClipToPadding(false);
        favPanel = round(0x24ffffff, d.radius + 12);
        favBox.setBackground(favPanel);
        FrameLayout.LayoutParams boxLp = new FrameLayout.LayoutParams(-1, dp(rowH));
        boxLp.topMargin = dp(yB);
        boxLp.leftMargin = dp(SIDE - 14);
        boxLp.rightMargin = dp(SIDE - 14);
        stage.addView(favBox, boxLp);
        dockList = createRow(favBox, new FrameLayout.LayoutParams(-1, -1), dockApps, true, d.favW, d.favH, false, 14, 14);

        gridList = createRow(stage, frameAt(-1, stageH - (yB + rowH - 6), yB + rowH - 6), otherApps, false, d.appW, d.appH, true, SIDE, SIDE);
        setStage(0f, 0f);
    }

    private FrameLayout.LayoutParams frameAt(int w, int hDp, int topDp) {
        FrameLayout.LayoutParams lp = new FrameLayout.LayoutParams(w, dp(hDp));
        lp.topMargin = dp(topDp);
        return lp;
    }

    private void setStageTarget(float p, float q) {
        if (targetP == p && targetQ == q) return;
        targetP = p; targetQ = q;
        if (stageAnim != null) stageAnim.cancel();
        final float fromP = stageP, fromQ = stageQ;
        stageAnim = ValueAnimator.ofFloat(0f, 1f);
        stageAnim.setDuration(400);
        stageAnim.setInterpolator(new DecelerateInterpolator(1.8f));
        stageAnim.addUpdateListener(new ValueAnimator.AnimatorUpdateListener() {
            @Override public void onAnimationUpdate(ValueAnimator a) {
                float f = (Float) a.getAnimatedValue();
                setStage(fromP + (targetP - fromP) * f, fromQ + (targetQ - fromQ) * f);
            }
        });
        stageAnim.start();
    }

    /** p: 0 favourites focused, 1 apps focused. q: 1 once the apps have scrolled past the second row. */
    private void setStage(float p, float q) {
        stageP = p;
        stageQ = q;
        favBox.setTranslationY(dp(stageDelta) * (1f - p) - dp(stageFavOut) * q);
        favBox.setAlpha(1f - q);
        favPanel.setAlpha((int) (255 * (1f - p)));
        FrameLayout.LayoutParams lp = (FrameLayout.LayoutParams) gridList.getLayoutParams();
        int top = Math.round(stageGridB - (stageGridB - stageGridC) * q);
        if (lp.topMargin != dp(top)) {
            lp.topMargin = dp(top);
            lp.height = dp(stageHeightDp - top);
            gridList.setLayoutParams(lp);
        }
        gridList.setTranslationY(dp(stageHide) * (1f - p));
        gridList.setAlpha(p);
        if (heroCopy != null) {
            heroCopy.setTranslationY(-dp(stageCopyShift) * p);
            heroCopy.setAlpha(1f - p);
        }
        if (heroArtHolder != null) heroArtHolder.setAlpha(1f - p);
    }

    private void buildHero(ViewGroup parent, ViewGroup.LayoutParams heroLp) {
        Design d = design;
        FrameLayout hero = new FrameLayout(this);
        hero.setPadding(dp(SIDE), dp(4), dp(SIDE), dp(10));
        hero.setClipChildren(false);
        parent.addView(hero, heroLp);
        boolean art = d.hero == 1 || d.hero == 4;
        if (art) {
            heroArt = new ImageView(this);
            heroArt.setScaleType(ImageView.ScaleType.CENTER_CROP);
            heroArt.setOutlineProvider(roundOutline(d.heroRadius));
            heroArt.setClipToOutline(true);
            heroArt.setBackground(round(d.tileBg, d.heroRadius));
            heroArtHolder = new FrameLayout(this);
            heroArtHolder.addView(heroArt, new FrameLayout.LayoutParams(-1, -1));
            hero.addView(heroArtHolder, new FrameLayout.LayoutParams(dp(d.heroW), dp(d.heroH), (d.hero == 1 ? Gravity.RIGHT : Gravity.LEFT) | Gravity.BOTTOM));
        }
        LinearLayout copy = new LinearLayout(this);
        copy.setOrientation(LinearLayout.VERTICAL);
        copy.setGravity(d.hero == 2 ? Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL : Gravity.BOTTOM);
        int copyGravity = d.hero == 2 ? Gravity.CENTER_HORIZONTAL : (d.hero == 4 ? Gravity.RIGHT : Gravity.LEFT);
        heroCopy = copy;
        hero.addView(copy, new FrameLayout.LayoutParams(d.hero == 2 ? -1 : dp(d.hero == 3 ? 820 : 520), -1, copyGravity));
        int align = d.hero == 2 ? Gravity.CENTER_HORIZONTAL : (d.hero == 4 ? Gravity.RIGHT : Gravity.LEFT);
        heroEyebrow = text("", 11, d.fg2, medium);
        heroEyebrow.setLetterSpacing(0.16f);
        heroEyebrow.setGravity(align);
        heroEyebrow.setVisibility(View.GONE);
        copy.addView(heroEyebrow, new LinearLayout.LayoutParams(-1, -2));
        heroTitle = text("", d.titleSize, d.fg, titleFace);
        heroTitle.setLetterSpacing(d.tracking);
        heroTitle.setGravity(align);
        heroTitle.setSingleLine(true);
        heroTitle.setEllipsize(android.text.TextUtils.TruncateAt.END);
        LinearLayout.LayoutParams titleLp = new LinearLayout.LayoutParams(-1, -2);
        titleLp.topMargin = dp(4);
        copy.addView(heroTitle, titleLp);
        heroHint = text("", 13, d.fg2, regular);
        heroHint.setGravity(align);
        LinearLayout.LayoutParams hintLp = new LinearLayout.LayoutParams(-1, -2);
        hintLp.topMargin = dp(6);
        copy.addView(heroHint, hintLp);
    }

    private RecyclerView addRow(LinearLayout page, String title, List<AppEntry> apps, boolean favorites, int w, int h, boolean legacy) {
        Design d = design;
        TextView head = text(d.upper ? title.toUpperCase(Locale.ROOT) : title, d.upper ? 11 : 13, d.upper ? d.fg2 : d.fg, medium);
        if (d.upper) head.setLetterSpacing(0.14f);
        head.setPadding(dp(SIDE), 0, 0, 0);
        LinearLayout.LayoutParams headLp = new LinearLayout.LayoutParams(-1, -2);
        headLp.topMargin = dp(4);
        page.addView(head, headLp);
        boolean grid = !favorites && d.grid;
        ViewGroup.LayoutParams lp = grid ? new LinearLayout.LayoutParams(-1, 0, 1) : new LinearLayout.LayoutParams(-1, dp(h + 34));
        return createRow(page, lp, apps, favorites, w, h, grid, SIDE, SIDE);
    }

    private RecyclerView createRow(ViewGroup parent, ViewGroup.LayoutParams lp, List<AppEntry> apps, boolean favorites, int w, int h, boolean grid, int padLeft, int padRight) {
        Design d = design;
        RecyclerView list = new RecyclerView(this);
        list.setClipChildren(grid);
        list.setClipToPadding(grid);
        int widthDp = (int) (getResources().getDisplayMetrics().widthPixels / getResources().getDisplayMetrics().density);
        int perRow = grid ? Math.max(1, (widthDp - 2 * SIDE + d.gap) / (w + d.gap)) : FAV_MAX;
        int rowWidth = parent == favBox ? widthDp - 2 * (SIDE - 14) : widthDp;
        int sideLeft = Math.max(0, (rowWidth - (perRow * w + (perRow - 1) * d.gap)) / 2);
        // The last card in a grid cell keeps its trailing gap, so the right padding gives it back to stay centred.
        int sideRight = grid ? Math.max(0, sideLeft - d.gap) : sideLeft;
        list.setPadding(dp(sideLeft), dp(grid ? 0 : 14), dp(sideRight), dp(grid ? 0 : 14));
        list.setOverScrollMode(View.OVER_SCROLL_NEVER);
        list.setItemAnimator(null);
        if (grid) {
            list.setLayoutManager(new androidx.recyclerview.widget.GridLayoutManager(this, perRow));
        } else {
            list.setLayoutManager(new LinearLayoutManager(this, RecyclerView.HORIZONTAL, false) {
                @Override public boolean canScrollHorizontally() { return false; }
            });
        }
        list.setAdapter(new AppAdapter(apps, favorites, w, h, grid));
        parent.addView(list, lp);
        return list;
    }

    private View.OnClickListener systemAction(final String action, final String error) {
        return new View.OnClickListener() {
            @Override public void onClick(View v) {
                try { startActivity(new Intent(action)); }
                catch (ActivityNotFoundException e) { Toast.makeText(MainActivity.this, error, Toast.LENGTH_SHORT).show(); }
            }
        };
    }

    private View pill(String label, String description, View.OnClickListener click) {
        final Design d = design;
        TextView button = text(label, 12, d.pillFg, medium);
        button.setGravity(Gravity.CENTER);
        button.setPadding(dp(16), 0, dp(16), 0);
        button.setBackground(round(d.pillBg, d.pillRadius));
        button.setFocusable(true);
        button.setContentDescription(description);
        button.setOnClickListener(click);
        button.setOnFocusChangeListener(new View.OnFocusChangeListener() {
            @Override public void onFocusChange(View v, boolean focused) {
                v.animate().cancel();
                v.animate().scaleX(focused ? 1.08f : 1f).scaleY(focused ? 1.08f : 1f).setDuration(160).start();
                v.setBackground(round(focused ? d.pillFocusBg : d.pillBg, d.pillRadius));
                ((TextView) v).setTextColor(focused ? d.pillFocusFg : d.pillFg);
            }
        });
        button.setOnKeyListener(new View.OnKeyListener() {
            @Override public boolean onKey(View v, int key, android.view.KeyEvent event) {
                if (event.getAction() == android.view.KeyEvent.ACTION_DOWN && key == android.view.KeyEvent.KEYCODE_DPAD_DOWN) { restoringFocus = false; restoreFocus(); return true; }
                return false;
            }
        });
        return button;
    }

    private final class AppAdapter extends RecyclerView.Adapter<AppHolder> {
        private final List<AppEntry> items;
        private final boolean favorites;
        private final int w, h;
        private final boolean grid;
        AppAdapter(List<AppEntry> items, boolean favorites, int w, int h, boolean grid) { this.items = items; this.favorites = favorites; this.w = w; this.h = h; this.grid = grid; setHasStableIds(true); }
        @Override public long getItemId(int position) { return items.get(position).packageName.hashCode(); }
        @Override public AppHolder onCreateViewHolder(ViewGroup parent, int type) {
            Design d = design;
            LinearLayout card = new LinearLayout(MainActivity.this);
            card.setOrientation(LinearLayout.VERTICAL);
            card.setGravity(Gravity.CENTER_HORIZONTAL);
            card.setClipChildren(false);
            card.setFocusable(true);
            card.setFocusableInTouchMode(true);
            RecyclerView.LayoutParams cardLp = new RecyclerView.LayoutParams(dp(w), -2);
            cardLp.rightMargin = dp(d.gap);
            if (grid) { cardLp.topMargin = dp(5); cardLp.bottomMargin = dp(5); }
            card.setLayoutParams(cardLp);
            ImageView art = new ImageView(MainActivity.this);
            art.setOutlineProvider(roundOutline(d.radius));
            art.setClipToOutline(true);
            card.addView(art, new LinearLayout.LayoutParams(dp(w), dp(h)));
            TextView label = text("", 11, d.fg, medium);
            label.setGravity(Gravity.CENTER);
            label.setSingleLine(true);
            label.setEllipsize(android.text.TextUtils.TruncateAt.END);
            LinearLayout.LayoutParams labelLp = new LinearLayout.LayoutParams(-1, dp(16));
            labelLp.topMargin = dp(8);
            label.setVisibility(View.GONE);
            card.addView(label, labelLp);
            return new AppHolder(card, art, label);
        }
        @Override public void onBindViewHolder(AppHolder holder, int position) {
            final Design d = design;
            AppEntry app = items.get(position);
            holder.itemView.setTag(app);
            holder.label.setText(app.label);
            int tile = d.tileBg;
            if (app.banner != null && !d.fit) {
                holder.art.setScaleType(ImageView.ScaleType.CENTER_CROP);
                holder.art.setPadding(0, 0, 0, 0);
                holder.art.setBackground(round(tile, d.radius));
                holder.art.setImageDrawable(app.banner);
            } else {
                boolean banner = app.banner != null;
                holder.art.setScaleType(ImageView.ScaleType.FIT_CENTER);
                int px = banner ? 6 : Math.max(10, w / 6), py = banner ? 6 : Math.max(8, h / 8);
                holder.art.setPadding(dp(px), dp(py), dp(px), dp(py));
                holder.art.setBackground(round(Color.alpha(tile) < 255 ? tile : blend(app.color, tile, 0.4f), d.radius));
                holder.art.setImageDrawable(banner ? app.banner : app.icon);
            }
            holder.art.setAlpha(app.installed ? 1f : 0.4f);
            holder.itemView.setContentDescription(app.label + (app.installed ? "" : ", no instalada"));
            holder.itemView.setOnClickListener(new View.OnClickListener() {
                @Override public void onClick(View v) { launch(app); }
            });
            holder.itemView.setLongClickable(true);
            holder.itemView.setOnLongClickListener(new View.OnLongClickListener() {
                @Override public boolean onLongClick(View v) { startMove(app, v); return true; }
            });
            holder.itemView.setRotation(0f);
            if (app == moving) wiggle(holder.itemView);
            holder.itemView.setOnFocusChangeListener(new View.OnFocusChangeListener() {
                @Override public void onFocusChange(View v, boolean focused) {
                    animateFocus(v, holder, focused);
                    if (focused) updateHero(app, favorites);
                }
            });
            holder.label.setAlpha(d.labelsAlways || holder.itemView.hasFocus() ? 1f : 0f);
        }
        @Override public int getItemCount() { return items.size(); }
    }

    private static final class AppHolder extends RecyclerView.ViewHolder {
        final ImageView art;
        final TextView label;
        AppHolder(View item, ImageView art, TextView label) { super(item); this.art = art; this.label = label; }
    }

    private static final class AppEntry {
        final String packageName;
        final CharSequence label;
        final Drawable icon;
        final Drawable banner;
        final boolean installed;
        final int color;
        AppEntry(String packageName, CharSequence label, Drawable icon, Drawable banner, boolean installed) {
            this.packageName = packageName; this.label = label; this.icon = icon; this.banner = banner; this.installed = installed;
            this.color = sampleColor(banner != null ? banner : icon);
        }
    }

    private void launch(AppEntry app) {
        if (!app.installed) {
            Toast.makeText(this, app.label + " no está instalada", Toast.LENGTH_SHORT).show();
            return;
        }
        PackageManager pm = getPackageManager();
        try {
            Intent chosen = pm.getLeanbackLaunchIntentForPackage(app.packageName);
            if (chosen == null) chosen = pm.getLaunchIntentForPackage(app.packageName);
            if (chosen == null) chosen = explicitLauncherIntent(pm, app.packageName, Intent.CATEGORY_LEANBACK_LAUNCHER);
            if (chosen == null) chosen = explicitLauncherIntent(pm, app.packageName, Intent.CATEGORY_LAUNCHER);
            if (chosen == null) throw new ActivityNotFoundException(app.packageName);
            chosen.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(chosen);
        } catch (ActivityNotFoundException e) {
            Toast.makeText(this, "No se pudo abrir " + app.label, Toast.LENGTH_SHORT).show();
        }
    }

    private Intent explicitLauncherIntent(PackageManager pm, String packageName, String category) {
        Intent query = new Intent(Intent.ACTION_MAIN).addCategory(category).setPackage(packageName);
        List<ResolveInfo> matches = pm.queryIntentActivities(query, 0);
        if (matches == null || matches.isEmpty()) return null;
        ResolveInfo match = matches.get(0);
        return new Intent(Intent.ACTION_MAIN).addCategory(category)
            .setClassName(packageName, match.activityInfo.name).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
    }

    private void updateHero(AppEntry app, boolean favorite) {
        Design d = design;
        lastColor = app.color;
        
        if (heroTitle != null) heroTitle.setText(d.upper ? app.label.toString().toUpperCase(Locale.ROOT) : app.label);
        if (heroHint != null) heroHint.setText(app.installed ? "" : "No instalada");
        if (heroArt != null) {
            boolean tall = d.fit || app.banner == null;
            heroArt.setScaleType(tall ? ImageView.ScaleType.FIT_CENTER : ImageView.ScaleType.CENTER_CROP);
            int px = app.banner == null ? d.heroW / 3 : (d.fit ? 10 : 0), py = app.banner == null ? d.heroH / 5 : (d.fit ? 10 : 0);
            heroArt.setPadding(dp(px), dp(py), dp(px), dp(py));
            heroArt.setBackground(round(tall ? (Color.alpha(d.tileBg) < 255 ? d.tileBg : blend(app.color, d.tileBg, 0.4f)) : d.tileBg, d.heroRadius));
            heroArt.setImageDrawable(app.banner != null ? app.banner : app.icon);
            heroArt.setAlpha(0.2f);
            heroArt.animate().cancel();
            heroArt.animate().alpha(app.installed ? 1f : 0.4f).setDuration(260).start();
        }
        ambient.setArt(app.banner != null ? app.banner : app.icon);
        int target = d.tint != 0 ? d.tint : app.color;
        if (ambientAnim != null) ambientAnim.cancel();
        ambientAnim = ValueAnimator.ofObject(new ArgbEvaluator(), ambient.color, target);
        ambientAnim.setDuration(420);
        ambientAnim.addUpdateListener(new ValueAnimator.AnimatorUpdateListener() {
            @Override public void onAnimationUpdate(ValueAnimator a) { ambient.color = (Integer) a.getAnimatedValue(); ambient.invalidate(); }
        });
        ambientAnim.start();
    }

    private void focusPosition(final RecyclerView list, final int pos) {
        list.scrollToPosition(pos);
        list.post(new Runnable() {
            @Override public void run() {
                RecyclerView.ViewHolder h = list.findViewHolderForAdapterPosition(pos);
                if (h != null) { h.itemView.requestFocus(); restoringFocus = false; return; }
                list.postDelayed(new Runnable() {
                    @Override public void run() {
                        RecyclerView.ViewHolder again = list.findViewHolderForAdapterPosition(pos);
                        if (again != null) again.itemView.requestFocus();
                        else if (list.getChildCount() > 0) list.getChildAt(0).requestFocus();
                        restoringFocus = false;
                    }
                }, 80);
            }
        });
    }

    // ---- Move mode: hold OK on an app, move it with the arrows, press OK or Back to drop it. ----

    private android.animation.ObjectAnimator wiggleAnim;

    private void startMove(AppEntry app, View tile) {
        moving = app;
        for (RecyclerView list : new RecyclerView[] { dockList, gridList }) {
            androidx.recyclerview.widget.DefaultItemAnimator animator = new androidx.recyclerview.widget.DefaultItemAnimator();
            animator.setMoveDuration(300);
            animator.setAddDuration(260);
            animator.setRemoveDuration(200);
            animator.setChangeDuration(0);
            animator.setSupportsChangeAnimations(false);
            list.setItemAnimator(animator);
        }
        wiggle(tile);
    }

    private void wiggle(View tile) {
        stopWiggle();
        tile.setRotation(-3f);
        wiggleAnim = android.animation.ObjectAnimator.ofFloat(tile, View.ROTATION, -3f, 3f);
        wiggleAnim.setDuration(110);
        wiggleAnim.setRepeatMode(ValueAnimator.REVERSE);
        wiggleAnim.setRepeatCount(ValueAnimator.INFINITE);
        wiggleAnim.start();
    }

    private void stopWiggle() {
        if (wiggleAnim == null) return;
        Object target = wiggleAnim.getTarget();
        wiggleAnim.cancel();
        if (target instanceof View) ((View) target).setRotation(0f);
        wiggleAnim = null;
    }

    private void endMove() {
        moving = null;
        stopWiggle();
        saveOrder();
        for (RecyclerView list : new RecyclerView[] { dockList, gridList }) {
            list.setItemAnimator(null);
            for (int i = 0; i < list.getChildCount(); i++) list.getChildAt(i).setRotation(0f);
        }
    }

    @Override public boolean dispatchKeyEvent(KeyEvent event) {
        if (moving == null) return super.dispatchKeyEvent(event);
        if (event.getAction() == KeyEvent.ACTION_DOWN) handleMoveKey(event.getKeyCode(), event.getRepeatCount());
        return true;
    }

    private void handleMoveKey(int key, int repeat) {
        if (key == KeyEvent.KEYCODE_DPAD_CENTER || key == KeyEvent.KEYCODE_ENTER || key == KeyEvent.KEYCODE_BACK || key == KeyEvent.KEYCODE_ESCAPE) {
            if (repeat == 0) endMove();
            return;
        }
        boolean inFav = dockApps.contains(moving);
        List<AppEntry> list = inFav ? dockApps : otherApps;
        int pos = list.indexOf(moving);
        int cols = inFav ? FAV_MAX : ((androidx.recyclerview.widget.GridLayoutManager) gridList.getLayoutManager()).getSpanCount();
        switch (key) {
            case KeyEvent.KEYCODE_DPAD_LEFT:
                if (pos > 0) reorder(list, pos, pos - 1);
                break;
            case KeyEvent.KEYCODE_DPAD_RIGHT:
                if (pos < list.size() - 1) reorder(list, pos, pos + 1);
                break;
            case KeyEvent.KEYCODE_DPAD_UP:
                if (inFav) break;
                if (pos >= cols) reorder(list, pos, pos - cols); else promote(pos);
                break;
            case KeyEvent.KEYCODE_DPAD_DOWN:
                if (inFav) { if (dockApps.size() > 1) demote(pos); }
                else if (pos + cols < list.size()) reorder(list, pos, pos + cols);
                else if (pos / cols < (list.size() - 1) / cols) reorder(list, pos, list.size() - 1);
                break;
            default:
        }
    }

    private void reorder(List<AppEntry> list, int from, int to) {
        RecyclerView rv = list == dockApps ? dockList : gridList;
        AppEntry item = list.remove(from);
        list.add(to, item);
        rv.getAdapter().notifyItemMoved(from, to);
        focusPosition(rv, to);
    }

    /** Apps -> favourites. A full favourites row pushes its last app back to the list. */
    private void promote(int from) {
        AppEntry item = otherApps.remove(from);
        gridList.getAdapter().notifyItemRemoved(from);
        if (dockApps.size() >= FAV_MAX) {
            AppEntry out = dockApps.remove(dockApps.size() - 1);
            dockList.getAdapter().notifyItemRemoved(dockApps.size());
            otherApps.add(0, out);
            gridList.getAdapter().notifyItemInserted(0);
        }
        int to = Math.min(from, dockApps.size());
        dockApps.add(to, item);
        dockList.getAdapter().notifyItemInserted(to);
        focusPosition(dockList, to);
    }

    /** Favourites -> apps, landing in the same column of the first row. */
    private void demote(int from) {
        AppEntry item = dockApps.remove(from);
        dockList.getAdapter().notifyItemRemoved(from);
        int to = Math.min(from, otherApps.size());
        otherApps.add(to, item);
        gridList.getAdapter().notifyItemInserted(to);
        focusPosition(gridList, to);
    }

    private void restoreFocus() {
        if (restoringFocus) return;
        restoringFocus = true;
        String saved = getPreferences(MODE_PRIVATE).getString("focused_package", dockApps.get(0).packageName);
        int pos = indexOf(dockApps, saved);
        if (pos >= 0) { focusPosition(dockList, pos); return; }
        pos = indexOf(otherApps, saved);
        if (pos >= 0) focusPosition(gridList, pos); else focusPosition(dockList, 0);
    }

    private int indexOf(List<AppEntry> apps, String pkg) {
        for (int i = 0; i < apps.size(); i++) if (apps.get(i).packageName.equals(pkg)) return i;
        return -1;
    }

    private void animateFocus(View v, AppHolder holder, boolean focused) {
        Design d = design;
        v.animate().cancel();
        v.animate().scaleX(focused ? d.scale : 1f).scaleY(focused ? d.scale : 1f)
            .setDuration(200).setInterpolator(new DecelerateInterpolator(1.6f)).start();
        v.setElevation(focused ? dp(10) : 0);
        holder.art.setElevation(focused ? dp(14) : 0);
        holder.art.setForeground(focused ? focusRing() : null);
        holder.label.animate().cancel();
        holder.label.animate().alpha(focused || d.labelsAlways ? 1f : 0f).setDuration(160).start();
        if (focused && v.getTag() instanceof AppEntry) {
            getPreferences(MODE_PRIVATE).edit().putString("focused_package", ((AppEntry) v.getTag()).packageName).apply();
        }
    }

    /** Focus ring for designs that define one (Taller, Neon, Retro); null otherwise, so focus is just the lift. */
    private Drawable focusRing() {
        Design d = design;
        if (d.strokeW <= 0) return null;
        GradientDrawable g = new GradientDrawable();
        g.setColor(Color.TRANSPARENT);
        g.setCornerRadius(dp(d.radius));
        g.setStroke(dp(d.strokeW), d.stroke);
        return g;
    }

    private TextView text(String value, float size, int color, Typeface face) {
        TextView t = new TextView(this);
        t.setText(value);
        t.setTextSize(size);
        t.setTextColor(color);
        t.setTypeface(face);
        t.setIncludeFontPadding(false);
        return t;
    }

    private GradientDrawable round(int color, int radius) {
        GradientDrawable d = new GradientDrawable();
        d.setColor(color);
        d.setCornerRadius(dp(radius));
        return d;
    }

    private ViewOutlineProvider roundOutline(final int radius) {
        return new ViewOutlineProvider() {
            @Override public void getOutline(View view, Outline outline) {
                outline.setRoundRect(0, 0, view.getWidth(), view.getHeight(), dp(radius));
            }
        };
    }

    private LinearLayout.LayoutParams wrap() { return new LinearLayout.LayoutParams(-2, dp(32)); }
    private int dp(float value) { return (int) (value * getResources().getDisplayMetrics().density + 0.5f); }

    private String wifiLabel() {
        try {
            WifiManager wifi = (WifiManager) getApplicationContext().getSystemService(WIFI_SERVICE);
            if (wifi != null && wifi.getConnectionInfo() != null) {
                String ssid = wifi.getConnectionInfo().getSSID();
                if (ssid != null && !ssid.isEmpty() && !ssid.equals("<unknown ssid>")) {
                    if (ssid.length() > 2 && ssid.startsWith("\"") && ssid.endsWith("\"")) ssid = ssid.substring(1, ssid.length() - 1);
                    return ssid.length() > 19 ? ssid.substring(0, 18) + "…" : ssid;
                }
            }
        } catch (SecurityException ignored) {}
        return "Wi-Fi";
    }

    private static int blend(int a, int b, float amount) {
        return Color.rgb(
            (int) (Color.red(a) * amount + Color.red(b) * (1 - amount)),
            (int) (Color.green(a) * amount + Color.green(b) * (1 - amount)),
            (int) (Color.blue(a) * amount + Color.blue(b) * (1 - amount)));
    }

    /** Dominant colour, weighted towards saturated pixels so white logo backgrounds do not wash it out. */
    private static int sampleColor(Drawable source) {
        if (source == null) return 0xff3a3a5c;
        Drawable drawable = source.getConstantState() == null ? source : source.getConstantState().newDrawable().mutate();
        Bitmap bitmap = Bitmap.createBitmap(24, 24, Bitmap.Config.ARGB_8888);
        Canvas canvas = new Canvas(bitmap);
        drawable.setBounds(0, 0, 24, 24);
        drawable.draw(canvas);
        float[] hsv = new float[3];
        double r = 0, g = 0, b = 0, total = 0;
        for (int y = 0; y < 24; y++) for (int x = 0; x < 24; x++) {
            int c = bitmap.getPixel(x, y);
            if (Color.alpha(c) < 200) continue;
            Color.colorToHSV(c, hsv);
            double w = 0.02 + hsv[1] * hsv[1] * hsv[2];
            r += Color.red(c) * w; g += Color.green(c) * w; b += Color.blue(c) * w; total += w;
        }
        bitmap.recycle();
        if (total == 0) return 0xff3a3a5c;
        Color.colorToHSV(Color.rgb((int) (r / total), (int) (g / total), (int) (b / total)), hsv);
        hsv[2] = Math.max(0.45f, Math.min(0.85f, hsv[2]));
        return Color.HSVToColor(hsv);
    }

    private static int withAlpha(int color, int alpha) { return (color & 0xffffff) | (alpha << 24); }

    private static int hueShift(int color, float degrees) {
        float[] hsv = new float[3];
        Color.colorToHSV(color, hsv);
        hsv[0] = (hsv[0] + degrees + 360f) % 360f;
        return Color.HSVToColor(hsv);
    }

    private static int shade(int color, float value) {
        float[] hsv = new float[3];
        Color.colorToHSV(color, hsv);
        hsv[2] = Math.max(0f, Math.min(1f, hsv[2] * value));
        return Color.HSVToColor(hsv);
    }

    /** Full-screen background, tinted by the focused app. Mode 0 uses the active design's own wash. */
    private final class AmbientView extends View {
        int color = 0xff3a3a5c;
        private Bitmap art;
        private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
        private final float[] starX = new float[140], starY = new float[140], starS = new float[140];

        AmbientView() {
            super(MainActivity.this);
            setFocusable(false);
            paint.setFilterBitmap(true);
            java.util.Random rnd = new java.util.Random(7);
            for (int i = 0; i < starX.length; i++) { starX[i] = rnd.nextFloat(); starY[i] = rnd.nextFloat(); starS[i] = rnd.nextFloat(); }
        }

        void setArt(Drawable source) {
            if (bgMode != 3 || source == null) return;
            Drawable drawable = source.getConstantState() == null ? source : source.getConstantState().newDrawable().mutate();
            Bitmap next = Bitmap.createBitmap(64, 36, Bitmap.Config.ARGB_8888);
            Canvas c = new Canvas(next);
            c.drawColor(color);
            int iw = drawable.getIntrinsicWidth(), ih = drawable.getIntrinsicHeight();
            if (iw > 0 && ih > 0 && ih * 64 < iw * 36) {
                int w = Math.round(36f * iw / ih);
                drawable.setBounds((64 - w) / 2, 0, (64 + w) / 2, 36);
            } else {
                drawable.setBounds(0, 0, 64, 36);
            }
            drawable.draw(c);
            if (art != null) art.recycle();
            art = next;
            invalidate();
        }

        @Override protected void onDraw(Canvas canvas) {
            int w = getWidth(), h = getHeight();
            switch (bgMode) {
                case 1: aurora(canvas, w, h); break;
                case 2: mesh(canvas, w, h); break;
                case 3: artwork(canvas, w, h); break;
                case 4: mountains(canvas, w, h); break;
                case 5: timeOfDay(canvas, w, h); break;
                case 6: geometric(canvas, w, h); break;
                case 7: workshop(canvas, w, h); break;
                case 8: space(canvas, w, h); break;
                default: classic(canvas, w, h);
            }
            paint.setShader(null);
        }

        private void glow(Canvas canvas, float x, float y, float r, int c, int alpha) {
            paint.setShader(new RadialGradient(x, y, r, withAlpha(c, alpha), withAlpha(c, 0), Shader.TileMode.CLAMP));
            canvas.drawRect(0, 0, getWidth(), getHeight(), paint);
        }

        private void fade(Canvas canvas, int w, int h, float from, int c, int alpha) {
            paint.setShader(new LinearGradient(0, h * from, 0, h, withAlpha(c, 0), withAlpha(c, alpha), Shader.TileMode.CLAMP));
            canvas.drawRect(0, 0, w, h, paint);
        }

        private void classic(Canvas canvas, int w, int h) {
            Design d = design;
            if (d.ambientMode == 3) return;
            if (d.ambientMode == 0) {
                paint.setShader(new LinearGradient(0, 0, 0, h * 0.8f, withAlpha(color, amp(0x5a)), withAlpha(color, 0), Shader.TileMode.CLAMP));
                canvas.drawRect(0, 0, w, h, paint);
                glow(canvas, w * 0.8f, h * 0.3f, w * 0.5f, color, amp(0x60));
            } else if (d.ambientMode == 1) {
                glow(canvas, w * 0.5f, h * 0.3f, w * 0.6f, color, amp(0x80));
            } else {
                paint.setShader(new LinearGradient(0, h, 0, h * 0.25f, withAlpha(color, amp(0x70)), withAlpha(color, 0), Shader.TileMode.CLAMP));
                canvas.drawRect(0, 0, w, h, paint);
            }
        }

        private int amp(int base) { return Math.min(255, (int) (base * design.ambient)); }

        private void aurora(Canvas canvas, int w, int h) {
            float t = (System.nanoTime() / 1_000_000_000f);
            int[] cols = { color, hueShift(color, 45), hueShift(color, -45) };
            for (int i = 0; i < 3; i++) {
                float x = w * (0.5f + 0.4f * (float) Math.sin(t * 0.22f + i * 2.1f));
                float y = h * (0.3f + 0.22f * (float) Math.cos(t * 0.17f + i * 1.7f));
                glow(canvas, x, y, w * 0.55f, cols[i], 0x90);
            }
            fade(canvas, w, h, 0.45f, design.bg, 0xd0);
            postInvalidateOnAnimation();
        }

        private void mesh(Canvas canvas, int w, int h) {
            glow(canvas, 0, 0, w * 0.75f, color, 0xa0);
            glow(canvas, w, 0, w * 0.7f, hueShift(color, 50), 0x90);
            glow(canvas, 0, h, w * 0.7f, hueShift(color, -50), 0x70);
            glow(canvas, w, h, w * 0.7f, hueShift(color, 100), 0x60);
            fade(canvas, w, h, 0.5f, design.bg, 0x90);
        }

        private void artwork(Canvas canvas, int w, int h) {
            if (art != null) {
                canvas.drawBitmap(art, null, new android.graphics.RectF(-w * 0.1f, -h * 0.1f, w * 1.1f, h * 1.1f), paint);
            }
            canvas.drawColor(0x66000000);
            fade(canvas, w, h, 0.45f, design.bg, 0xd8);
        }

        private void mountains(Canvas canvas, int w, int h) {
            paint.setShader(new LinearGradient(0, 0, 0, h * 0.7f, shade(color, 0.35f), blend(color, 0xff1a1a24, 0.5f), Shader.TileMode.CLAMP));
            canvas.drawRect(0, 0, w, h, paint);
            glow(canvas, w * 0.72f, h * 0.3f, w * 0.22f, 0xffffe2b0, 0xc0);
            android.graphics.Path path = new android.graphics.Path();
            for (int layer = 0; layer < 3; layer++) {
                path.reset();
                float base = h * (0.5f + 0.12f * layer);
                path.moveTo(0, h);
                for (int x = 0; x <= w; x += 8) {
                    float u = x / (float) w;
                    float y = base - h * 0.1f * (float) (Math.sin(u * 5f + layer * 2f) * 0.6 + Math.sin(u * 11f + layer * 5f) * 0.3 + Math.sin(u * 23f + layer) * 0.1);
                    path.lineTo(x, y);
                }
                path.lineTo(w, h);
                path.close();
                paint.setShader(null);
                paint.setColor(blend(shade(color, 0.5f), 0xff050507, 0.55f - layer * 0.2f));
                canvas.drawPath(path, paint);
            }
        }

        private void timeOfDay(Canvas canvas, int w, int h) {
            java.util.Calendar cal = java.util.Calendar.getInstance();
            float hour = cal.get(java.util.Calendar.HOUR_OF_DAY) + cal.get(java.util.Calendar.MINUTE) / 60f;
            int top, mid;
            if (hour < 6 || hour >= 21) { top = 0xff070a22; mid = 0xff1b2358; }
            else if (hour < 9) { top = 0xff2a2150; mid = 0xffc9694a; }
            else if (hour < 17) { top = 0xff0d3566; mid = 0xff3f8ccb; }
            else if (hour < 20) { top = 0xff2a1745; mid = 0xffe0572f; }
            else { top = 0xff0b1030; mid = 0xff3a2a78; }
            paint.setShader(new LinearGradient(0, 0, 0, h, new int[] { top, mid, 0xff08080c }, new float[] { 0f, 0.5f, 1f }, Shader.TileMode.CLAMP));
            canvas.drawRect(0, 0, w, h, paint);
            boolean night = hour < 6 || hour >= 20;
            float u = night ? ((hour + 4) % 24) / 10f : (hour - 6) / 14f;
            glow(canvas, w * (0.1f + 0.8f * Math.max(0, Math.min(1, u))), h * 0.22f, w * 0.12f, night ? 0xffdfe6ff : 0xffffe9b8, 0xd0);
        }

        private void geometric(Canvas canvas, int w, int h) {
            glow(canvas, w * 0.85f, h * 0.25f, w * 0.7f, color, 0x70);
            paint.setStyle(Paint.Style.STROKE);
            paint.setStrokeWidth(dp(1.5f));
            for (int i = 1; i <= 9; i++) {
                paint.setColor(withAlpha(color, Math.max(0x10, 0x80 - i * 12)));
                canvas.drawCircle(w * 0.85f, h * 0.25f, dp(46) * i, paint);
            }
            paint.setStyle(Paint.Style.FILL);
            fade(canvas, w, h, 0.5f, design.bg, 0xc0);
        }

        private void workshop(Canvas canvas, int w, int h) {
            canvas.drawColor(0xff1b1a18);
            android.graphics.Path cone = new android.graphics.Path();
            cone.moveTo(w * 0.42f, 0); cone.lineTo(w * 0.58f, 0); cone.lineTo(w * 0.95f, h); cone.lineTo(w * 0.05f, h); cone.close();
            paint.setShader(new LinearGradient(0, 0, 0, h * 0.85f, 0x66e8703f, 0x00e8703f, Shader.TileMode.CLAMP));
            canvas.drawPath(cone, paint);
            glow(canvas, w * 0.5f, 0, w * 0.35f, 0xffe8703f, 0x70);
            paint.setShader(null);
            paint.setColor(0xffe8703f);
            canvas.drawCircle(w * 0.5f, 0, dp(5), paint);
        }

        private void space(Canvas canvas, int w, int h) {
            canvas.drawColor(0xff02030a);
            glow(canvas, w * 0.75f, h * 0.2f, w * 0.5f, color, 0x60);
            glow(canvas, w * 0.15f, h * 0.7f, w * 0.45f, hueShift(color, 70), 0x40);
            float t = System.nanoTime() / 1_000_000_000f;
            paint.setShader(null);
            for (int i = 0; i < starX.length; i++) {
                float tw = 0.55f + 0.45f * (float) Math.sin(t * (0.6f + starS[i]) + i);
                paint.setColor(withAlpha(0xffffffff, (int) (60 + 190 * starS[i] * tw)));
                canvas.drawCircle(starX[i] * w, starY[i] * h, dp(0.5f + 1.2f * starS[i]), paint);
            }
            postInvalidateOnAnimation();
        }
    }
}
