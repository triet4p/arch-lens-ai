use rfd::FileDialog;
use std::fs;
use std::sync::Mutex;
use tauri::{Manager, State};
use tauri_plugin_shell::process::CommandEvent;
use tauri_plugin_shell::ShellExt;

// Trạng thái để kiểm soát việc khởi động Sidecar
struct AppState {
    sidecar_started: Mutex<bool>,
}

#[tauri::command]
async fn start_sidecar(
    app_handle: tauri::AppHandle,
    state: State<'_, AppState>,
) -> Result<String, String> {
    let mut started = state.sidecar_started.lock().unwrap();

    // Nếu đã khởi động rồi thì không làm gì thêm
    if *started {
        return Ok("Sidecar already running".into());
    }

    let handle = app_handle.clone();
    let sidecar_command = handle
        .shell()
        .sidecar("arch-lens-ai-backend")
        .map_err(|error| format!("Unable to resolve sidecar: {error}"))?;
    let (mut rx, _child) = sidecar_command
        .spawn()
        .map_err(|error| format!("Failed to spawn sidecar: {error}"))?;

    // Spawn Sidecar trong một luồng riêng
    tauri::async_runtime::spawn(async move {
        while let Some(event) = rx.recv().await {
            match event {
                CommandEvent::Stdout(line) => {
                    let text = String::from_utf8_lossy(&line);
                    log::info!(target: "python", "{}", text.trim());
                }
                CommandEvent::Stderr(line) => {
                    let text = String::from_utf8_lossy(&line);
                    log::error!(target: "python", "{}", text.trim());
                }
                _ => {}
            }
        }
    });

    *started = true;
    Ok("Sidecar start command issued".into())
}

#[tauri::command]
async fn save_markdown_report(default_file_name: String, content: String) -> Result<String, String> {
    let path = FileDialog::new()
        .set_file_name(&default_file_name)
        .add_filter("Markdown", &["md"])
        .save_file()
        .ok_or_else(|| "Save cancelled".to_string())?;

    fs::write(&path, content).map_err(|error| format!("Unable to write report: {error}"))?;
    Ok(path.display().to_string())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .manage(AppState {
            sidecar_started: Mutex::new(false),
        })
        .plugin(
            tauri_plugin_log::Builder::new()
                .level(tauri_plugin_log::log::LevelFilter::Info)
                .build(),
        )
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_opener::init())
        .setup(|app| {
            // Lấy window chính
            let Some(window) = app.get_webview_window("main") else {
                log::error!("Main window not found during setup");
                return Ok(());
            };

            // Phóng to full màn hình
            if let Err(error) = window.maximize() {
                log::warn!("Unable to maximize window: {}", error);
            }

            // Hiện cửa sổ lên sau khi đã phóng to xong
            if let Err(error) = window.show() {
                log::warn!("Unable to show window: {}", error);
            }

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![start_sidecar, save_markdown_report])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
