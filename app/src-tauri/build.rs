fn main() {
    // The executable's Windows resources are generated here. Cargo otherwise
    // reuses the old .res when only the ICO changes, leaving a stale taskbar
    // and installer icon in an otherwise updated application.
    println!("cargo:rerun-if-changed=icons/icon.ico");
    tauri_build::build()
}
