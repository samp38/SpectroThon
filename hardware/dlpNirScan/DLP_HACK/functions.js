function generate_script_file (root)

function ref_controls (root) {
	generate_script_file
	run_reference_scan
}

function run_reference_scan (not root) {
	generate_script_file
	check_ref_scan_completed
}

function check_ref_scan_completed (not root, recursive) {
	show_scan_results
}

function generate_scaninfo_files (not root) {
	write_spectrumdatafile
}

function write_spectrumdatafile (not root)

function run_sample_scan (not root) {
	generate_script_file
	check_scan_completed 
}

function show_scan_results (not root) (= show_results)

function check_scan_completed (not root, recursive) {
	generate_scaninfo_files
}

function run_scan_fun (root) {
	run_sample_scan
	apply_settings
	get_lambda_values
}

function Download (root)

// Bonus

function view_settings (root) {
	read_settings
}

function read_settings (not root)

function apply_settings (not root)

function get_lambda_values (not root)

function display_warning (root)

function generate_patterns (root) {
	apply_settings
}

