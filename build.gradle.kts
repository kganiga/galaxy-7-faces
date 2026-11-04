import com.android.build.api.dsl.ApplicationExtension

plugins {
    id("com.android.application") version "8.9.1" apply false
}

// Shared settings for every watch face module. Per-face values (package, versionName)
// live in faces/<name>/face.properties, so a face's build.gradle.kts is one line.
//
// Signing: CI passes a private keystore through SIGNING_* env vars (repo secrets) when
// they exist; otherwise the committed signing/sideload.keystore is used, so every build
// has the same signature and installs as an update over the previous one.
val signingStore: File = System.getenv("SIGNING_KEYSTORE_PATH")?.let { file(it) }
    ?: rootProject.file("signing/sideload.keystore")
val buildNumber: Int = System.getenv("GITHUB_RUN_NUMBER")?.toIntOrNull() ?: 1

subprojects {
    plugins.withId("com.android.application") {
        val face = java.util.Properties().apply {
            project.file("face.properties").reader().use { load(it) }
        }
        extensions.configure<ApplicationExtension> {
            namespace = face.getProperty("package")
            compileSdk = 35

            defaultConfig {
                applicationId = face.getProperty("package")
                versionName = face.getProperty("versionName")
                // Watch Face Format v2 needs Wear OS 5 (API 34), e.g. Galaxy Watch 7.
                minSdk = 34
                targetSdk = 34
                versionCode = buildNumber
            }

            signingConfigs {
                create("sideload") {
                    storeFile = signingStore
                    storePassword = System.getenv("SIGNING_STORE_PASSWORD") ?: "android"
                    keyAlias = System.getenv("SIGNING_KEY_ALIAS") ?: "debug"
                    keyPassword = System.getenv("SIGNING_KEY_PASSWORD") ?: "android"
                }
            }

            buildTypes {
                getByName("release") {
                    // A WFF APK has no code, so there is nothing to minify or shrink.
                    isMinifyEnabled = false
                    signingConfig = signingConfigs.getByName("sideload")
                }
            }
        }
    }
}
