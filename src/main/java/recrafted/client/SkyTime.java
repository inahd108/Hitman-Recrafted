package recrafted.client;

/**
 * Lets a dev harness photograph a fixed-time dimension (Corvara is pinned to late morning) at another hour.
 * Negative means "no override", which is always the case outside the dev harness.
 */
public final class SkyTime {
    public static volatile long override = -1;

    private SkyTime() {}
}
