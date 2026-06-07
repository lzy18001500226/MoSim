use std::env;
use std::process::Command;

fn main() {
    let script_path = format!("{}/scripts/release-tag.sh", env!("CARGO_MANIFEST_DIR"));
    let arguments: Vec<String> = env::args().skip(1).collect();

    let status = match Command::new(&script_path).args(&arguments).status() {
        Ok(status) => status,
        Err(error) => {
            eprintln!("Failed to execute {}: {}", script_path, error);
            std::process::exit(1);
        }
    };

    match status.code() {
        Some(code) => std::process::exit(code),
        None => std::process::exit(1),
    }
}
