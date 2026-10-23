package dev.clean.tvlauncher;

/** User-editable launcher layout. Keep dock package names in preferred order. */
public final class LauncherConfig {
    private LauncherConfig() {}

    public static final int GRID_COLUMNS = 6;
    /** Solid black wallpaper color; edit this hex value to change the background. */
    public static final int BACKGROUND_COLOR = 0xff050507;
    public static final String[] DOCK_PACKAGES = {
        "org.jellyfin.androidtv",
        "com.google.android.youtube.tv",
        "com.netflix.ninja",
        "com.amazon.amazonvideo.livingroom",
        "com.movistarplus.androidtv"
    };
    public static final String[] DOCK_FALLBACK_LABELS = {
        "Jellyfin", "YouTube", "Netflix", "Prime Video", "Movistar Plus+"
    };
}
