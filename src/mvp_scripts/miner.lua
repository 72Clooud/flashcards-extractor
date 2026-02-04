local utils = require 'mp.utils'

local function miner_current_line()
    local text = mp.get_property("sub-text")
    local path = mp.get_property("path")
    local start_time = mp.get_property_number("sub-start")
    local end_time = mp.get_property_number("sub-end")

    local script_dir = mp.get_script_directory() or "."

    local log_path = utils.join_path(script_dir, "../../mining_queue.txt")

    if not text or text == "" then
        mp.osd_message("Error: No subtitle text found")
        return
    end

    if not start_time or not end_time then
        mp.osd_message("Error: Failed to retrieve subtitle timing")
        return
    end

    if not path then
        mp.osd_message("Error: No path to file")
        return
    end

    local clean_text = text:gsub("\n", " ")
    local log_line = string.format("%s|%.3f|%.3f|%s\n", path, start_time, end_time, clean_text)

    local file = io.open(log_path, "a")
    if file then
        file:write(log_line)
        file:close()
        mp.osd_message("Subtitle logged!")
    else
        mp.osd_message("Failed to open mining_queue.txt")
    end
end

mp.add_key_binding("g", "log_subtitle", miner_current_line)