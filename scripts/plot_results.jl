#!/usr/bin/env julia

# Lightweight placeholder for report figure generation.
# Prefer Syslab plotting APIs when available; this script currently writes a
# figure manifest so automated workflows have a stable output contract.
#
# Usage:
#   julia scripts/plot_results.jl results/{group}/{scene}/raw/figure8.csv results/{group}/{scene}/figures

using Dates

function main()
    if length(ARGS) < 2
        println(stderr, "Usage: julia scripts/plot_results.jl <raw_csv> <figure_dir>")
        exit(2)
    end
    raw_csv = ARGS[1]
    figure_dir = ARGS[2]
    mkpath(figure_dir)
    manifest = joinpath(figure_dir, "figure_manifest.md")
    open(manifest, "w") do io
        println(io, "# Figure Manifest")
        println(io)
        println(io, "- Generated: `$(now())`")
        println(io, "- Raw file: `$raw_csv`")
        println(io, "- Status: `placeholder`")
        println(io)
        println(io, "Expected report figures:")
        println(io)
        println(io, "- `trajectory_3d.png`")
        println(io, "- `position_error.png`")
        println(io, "- `attitude.png`")
        println(io, "- `control_input.png`")
        println(io, "- `metrics_bar.png`")
        println(io)
        println(io, "Use Syslab plotting APIs or Sysplorer `plot_manager` to generate image files, then update this manifest.")
    end
    println("Figure manifest written: $manifest")
end

main()
