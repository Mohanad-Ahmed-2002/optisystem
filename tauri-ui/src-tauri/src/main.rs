#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::{fs, process::Command, thread, time::Duration};
#[cfg(target_os = "windows")]
use std::os::windows::process::CommandExt;

use tauri_plugin_dialog::{DialogExt, MessageDialogBuilder, MessageDialogKind};
use base64::{engine::general_purpose, Engine as _};

fn sha256(input: &str) -> String {
    use sha2::{Digest, Sha256};
    let mut hasher = Sha256::new();
    hasher.update(input.as_bytes());
    format!("{:x}", hasher.finalize())
}

fn check_license() -> bool {
    let exe_path = std::env::current_exe().unwrap();
    let license_path = exe_path.parent().unwrap().join("license_uuid.key");

    if !license_path.exists() {
        return false;
    }

    let encoded = fs::read_to_string(&license_path).unwrap_or_default();

    let decoded_bytes = match general_purpose::STANDARD.decode(encoded.trim()) {
        Ok(bytes) => bytes,
        Err(_) => return false,
    };

    let decoded = match String::from_utf8(decoded_bytes) {
        Ok(text) => text,
        Err(_) => return false,
    };


    let parts: Vec<&str> = decoded.trim().split('|').collect();
    if parts.len() != 3 {
        return false;
    }

    let uuid = parts[0];
    let expiry = parts[1];
    let signature = parts[2];

    let expected_signature = sha256(&format!("{}|{}", uuid, expiry));
    if signature != expected_signature {
        return false;
    }

    if let Ok(expiry_date) = chrono::NaiveDate::parse_from_str(expiry, "%Y-%m-%d") {
        let today = chrono::Local::now().naive_local().date();
        return today <= expiry_date;
    }

    false
}

fn is_django_ready() -> bool {
    reqwest::blocking::get("http://127.0.0.1:8000").is_ok()
}

fn main() {
    #[cfg(target_os = "windows")]
    const CREATE_NO_WINDOW: u32 = 0x08000000;

    tauri::Builder::default()
        .setup(|app| {
            let dialog = app.dialog();

            if !check_license() {
                MessageDialogBuilder::new(
                    dialog.to_owned(),
                    "الترخيص غير صالح",
                    "البرنامج غير مفعل أو انتهت صلاحيته. الرجاء التواصل مع الدعم.",
                )
                .kind(MessageDialogKind::Error)
                .show(|_| {
                    std::process::exit(1);
                });

                return Ok(());
            }

            // ✅ شغّل Django
            let _ = Command::new("D:\\projects\\optisystem\\venv\\Scripts\\python.exe")
                .arg("manage.py")
                .arg("runserver")
                .current_dir("D:\\projects\\optisystem\\optica")
                .creation_flags(CREATE_NO_WINDOW)
                .spawn();

            for _ in 0..30 {
                if is_django_ready() {
                    break;
                }
                thread::sleep(Duration::from_secs(1));
            }

            Ok(())
        })
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        .build(tauri::generate_context!())
        .expect("فشل في تشغيل التطبيق")
        .run(|_app_handle, _event| {});
}
