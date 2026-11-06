Global Engineering Rules — Galaxy Watch 7 Watch Faces

These instructions are mandatory for every existing, new, modified, or regenerated watch face in this repository.

1. Target Device and Platform

- Primary target: Samsung Galaxy Watch 7.
- Target Wear OS 5 and the appropriate Watch Face Format (WFF) version.
- Prefer the latest WFF version supported by the target device and toolchain.
- Use WFF as the default architecture for new watch faces.
- Do not introduce deprecated Jetpack Watch Face or Wearable Support Library APIs for new faces.
- Inspect the existing project before changing its architecture.
- Preserve existing watch-face designs, themes, colors, and visual identity unless explicitly asked to redesign them.
- Ensure compatibility with the actual Galaxy Watch 7 circular display and its safe areas.

2. Global Auto-Layout System — Mandatory

Every watch face must use a responsive layout strategy.

Never assume that fixed coordinates will work for every content variation.

Requirements:

- Calculate available display space before positioning elements.
- Respect circular display boundaries and screen-safe areas.
- Account for screen margins, rounded edges and burn-in protection.
- Maintain balanced spacing between all elements.
- Avoid overlapping time, date, complications, icons and decorative graphics.
- Use reusable layout definitions and shared design tokens.
- Maintain consistent alignment and visual hierarchy.
- Automatically adjust font sizes and element positions when content changes.
- Ensure all elements remain inside the visible screen area.

Dynamic text handling

This is a critical requirement.

- Never allow text to be silently clipped.
- Use WFF automatic text sizing wherever supported.
- Set sensible minimum and maximum font sizes.
- Calculate text dimensions against available width.
- Handle long weekday names, dates, numbers and complication values.
- Use adaptive positioning when text becomes longer.
- Use compact formatting only when necessary and preserve the meaning.
- Prefer wrapping where the component and available space support it.
- Never use scrolling marquee text as a workaround.
- Never hide important information to solve a layout problem.
- If the content cannot fit, use a deliberate fallback presentation rather than clipping it.

Examples that must be handled:

- Wednesday versus Mon
- September versus May
- 99,999 versus 1,250 steps
- 98% versus 8%
- Long weather descriptions
- Battery percentage and charging status
- Heart-rate values
- Long complication labels

Acceptance criterion: No visible text should be cut off, clipped by the circular screen, or overlap another component under supported content variations.

3. Complete Complication Framework

Every watch face must have a properly designed and configurable complication system.

Use the maximum supported capacity of up to eight complication slots where the design can accommodate them.

Support appropriate complication data types, including:

- SHORT_TEXT
- LONG_TEXT
- RANGED_VALUE
- MONOCHROMATIC_IMAGE
- SMALL_IMAGE
- PHOTO_IMAGE
- GOAL_PROGRESS
- WEIGHTED_ELEMENTS

Only use types supported by the selected WFF version.

Complication requirements

- Every intended slot must be independently configurable.
- Provide suitable default layouts for unconfigured slots.
- Support empty and no-data states.
- Never display placeholder values as if they were real measurements.
- Handle unavailable data gracefully.
- Support system-provided complication sources.
- Ensure complication content automatically fits its allocated region.
- Provide clear visual distinction between complication values and labels.
- Make complication slots touch-friendly.
- Do not let complications overlap the central clock or other elements.
- Test all supported complication types, not just the default one.

Do not force eight visible complications into a design that cannot accommodate them cleanly. Preserve the design's visual hierarchy while providing the maximum practical configurable slots.

4. Dedicated AOD Optimization

Every watch face must have two intentionally designed presentations:

1. Interactive mode.
2. Always-On Display (AOD) mode.

Do not simply reuse the full interactive presentation in AOD.

Interactive mode

- Full visual design.
- Appropriate colors and gradients.
- Detailed graphics.
- Complete complication presentation.
- Smooth transitions where supported.
- High legibility.

AOD mode

- Predominantly black background.
- Minimal pixel illumination.
- High-contrast, readable time.
- Simplified graphics.
- Reduced decorative elements.
- No unnecessary animations.
- No rapidly updating elements.
- No seconds unless explicitly justified and supported.
- Use static or appropriate fallback values for frequently changing measurements.
- Preserve the overall visual identity of the original face.
- Maintain stable element positions between modes.
- Respect burn-in protection and ambient update restrictions.

Optimize AOD for battery consumption without sacrificing time readability.

5. Sensor and Battery Optimization

Use device sensors intelligently. Never continuously poll sensors just to populate a watch face.

Important distinction: WFF watch faces are declarative. They do not directly execute arbitrary sensor-reading code. Use supported system complication providers or a separately implemented, permission-aware data-source application when custom sensor integration is genuinely required.

Sensor policy

For every requested sensor:

1. Check whether Wear OS or Samsung already provides the information through an existing complication source.
2. Prefer existing system data sources.
3. Only implement a custom data source when there is a genuine functional requirement.
4. Request only necessary permissions.
5. Respect background execution and sensor restrictions.
6. Use appropriate sampling intervals and batching.
7. Avoid continuous sensor subscriptions.
8. Avoid unnecessary wake-ups.
9. Cache data where appropriate.
10. Handle unavailable, stale and permission-denied data.

Sensor-specific rules

Heart rate

- Prefer the system health/heart-rate complication.
- Never continuously measure heart rate simply to display a number.
- Distinguish live measurements from historical measurements.
- Display unavailable or stale data honestly.

Steps

- Prefer the system step-count complication.
- Do not implement an independent step counter if an existing system source meets the requirement.
- Avoid unnecessary sensor polling.

Calories and activity

- Prefer system health and activity data sources.
- Never calculate misleading values from incomplete sensor data.

GPS and location

- Do not activate GPS continuously for decorative watch-face information.
- Use location only when a genuine feature requires it.

Accelerometer and gyroscope

- Do not keep motion sensors active without a meaningful use case.
- Prefer system-managed information when available.

Battery

- Prefer the system battery complication.
- Avoid frequent custom battery polling.

Weather

- Prefer an existing weather complication source.
- Do not introduce continuous network requests.

Never assume that Galaxy Watch 7 exposes every sensor through an unrestricted API.

6. No Duplicate Code — Shared Architecture

Maintain a clean, reusable architecture across the entire repository.

Establish shared definitions for:

- Typography
- Colors
- Spacing
- Screen-safe areas
- Layout rules
- Complication configurations
- AOD presentation
- Interactive presentation
- Icons and graphical assets
- Formatting conventions
- Common visual patterns
- Validation rules

Rules:

- Never copy and paste existing implementations unnecessarily.
- Reuse existing utilities before creating new ones.
- Avoid duplicate XML definitions where shared generation or templates are appropriate.
- Avoid duplicate sensor services.
- Avoid duplicate data-source implementations.
- Avoid multiple competing formatting utilities.
- Keep watch-face-specific styling separate from shared infrastructure.
- Use clear naming conventions.
- Keep configuration and presentation separate.
- Remove dead code and unused assets.
- Avoid introducing unnecessary dependencies.

If WFF requires separate declarative definitions, use reusable templates or generation tooling where appropriate. Do not invent unsupported runtime imports or assume XML files can directly share arbitrary code.

7. Visual Quality Standards

Every face must look professionally designed on an actual Galaxy Watch 7.

Mandatory checks:

- Balanced composition.
- Consistent typography.
- Proper text hierarchy.
- No overlapping components.
- No cut-off text.
- No elements outside safe boundaries.
- Consistent margins.
- Proper contrast.
- Readable complications.
- Legible AOD.
- No unnecessary decorative clutter.
- No visual inconsistencies between display modes.

Never sacrifice readability just to preserve a decorative element.

8. Existing Watch Face Retrofitting

These rules apply retroactively to ALL existing watch faces.

Before making changes:

1. Discover every existing watch face in the repository.
2. Identify its current implementation format.
3. Inspect its layouts, complication slots and AOD design.
4. Identify text clipping and overlapping elements.
5. Identify duplicated code and assets.
6. Identify unnecessary sensor usage.
7. Identify battery and rendering inefficiencies.
8. Record the issues before modifying files.

Then systematically update every existing watch face.

Do not only fix the latest watch face.

Do not discard an existing design and generate a replacement without justification.

Preserve the original design while upgrading its engineering quality.

9. Mandatory Testing

Every watch face must pass the following validation scenarios.

Test| Expected result
Short text| Correct alignment
Long text| Automatically adapts
Large numbers| No clipping
Small numbers| No awkward spacing
Empty complication| Clean empty state
Missing data| Honest fallback
All complication types| Correct rendering
Interactive mode| Full presentation
AOD mode| Optimized presentation
Circular boundaries| No overflow
Burn-in protection| Safe positioning
Battery optimization| No unnecessary updates
Sensor unavailable| Graceful fallback
Screen transition| No layout jump

Test using representative short and long values, different complication providers, and actual Galaxy Watch 7 hardware wherever possible.

Run the relevant WFF validation and memory checks before declaring a face complete.

Do not claim that a face is fully tested if only its XML has been inspected.

10. Claude Code Workflow

Before creating or modifying ANY watch face:

1. Read this entire CLAUDE.md file.
2. Inspect the existing repository architecture.
3. Identify reusable components and utilities.
4. Review the original watch-face design.
5. Define its interactive and AOD layouts.
6. Plan its complication slots.
7. Check text sizing and safe-area constraints.
8. Check whether any custom sensor integration is actually necessary.
9. Implement using shared architecture.
10. Validate the resulting watch face.
11. Report any remaining limitations.

Never generate a watch face using isolated assumptions without inspecting the existing project.

Never declare completion merely because the build succeeds.

11. Definition of Done

A watch face is complete only when:

- It retains its intended visual identity.
- All text is legible and protected against clipping.
- Layout adapts to different content lengths.
- Complication slots are properly configured.
- Supported complication data types render correctly.
- Interactive and AOD modes are optimized independently.
- Sensor usage is justified and power-efficient.
- No unnecessary duplicate implementation exists.
- The WFF validation passes.
- Remaining limitations are documented.

Final Global Rule

These requirements are repository-wide engineering standards, not optional recommendations.

Apply them to every watch face created in the past, every watch face being modified now, and every watch face created in the future.

When instructions conflict with visual design, prioritize:

1. Correctness and data integrity.
2. Readability and no clipping.
3. Battery efficiency.
4. Complete complication functionality.
5. Original visual design.
6. Decorative effects.

Do not silently compromise a higher-priority requirement to satisfy a lower-priority one.