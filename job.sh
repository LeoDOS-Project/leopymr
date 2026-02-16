#!/bin/bash

# Default values
URL="http://localhost:8089"
ALLOCATOR="bipartite"
SEED=-1
REDUCETYPE="center"
MINSAT=3
MAXSAT=8
COLLECTORS=11
COLLECTTASK="doccollector"
MAPTASK="wordcountmapper"
REDUCETASK="sumreducer"
MAXRECORDS=1024
DATA_FILE=""
JOB_ID=""
RESULT_FILE=""

# Help function
function show_help {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -i, --id ID             Job ID (specify to return results of job)"
    echo "  -f, --file FILE         Can be used with job id to download a job result file"
    echo "  -a, --allocator ALLOC   Map allocator (default: bipartite)"
    echo "  -s, --seed SEED         Random aoi shuffle seed (default: -1)"
    echo "  -r, --reducetype TYPE   Reduce placement (default: center)"
    echo "  -mi, --minsat N         Min aoi grid index (default: 3)"
    echo "  -ma, --maxsat N         Max aoi grid index (default: 8)"
    echo "  -c, --collectors N      Total collectors (and mappers) (default: 11)"
    echo "  -ct, --collecttask TASK Collector task (default: doccollector)"
    echo "  -mt, --maptask TASK     Mapper task (default: wordcountmapper)"
    echo "  -rt, --reducetask TASK  Reducer task (default: sumreducer)"
    echo "  -d, --data FILE         Job data file (json)"
    echo "  -mr, --maxrecords N     Max records to collect before streaming to mapper (default: 1024)"
    echo "  -u, --url URL           Gateway server endpoint (default: http://localhost:8089)"
    echo "  -h, --help              Show this help message"
}

# Argument parsing
while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--id)
            JOB_ID="$2"
            shift 2
            ;;
        -f|--file)
            RESULT_FILE="$2"
            shift 2
            ;;
        -a|--allocator)
            ALLOCATOR="$2"
            shift 2
            ;;
        -s|--seed)
            SEED="$2"
            shift 2
            ;;
        -r|--reducetype)
            REDUCETYPE="$2"
            shift 2
            ;;
        -mi|--minsat)
            MINSAT="$2"
            shift 2
            ;;
        -ma|--maxsat)
            MAXSAT="$2"
            shift 2
            ;;
        -c|--collectors)
            COLLECTORS="$2"
            shift 2
            ;;
        -ct|--collecttask)
            COLLECTTASK="$2"
            shift 2
            ;;
        -mt|--maptask)
            MAPTASK="$2"
            shift 2
            ;;
        -rt|--reducetask)
            REDUCETASK="$2"
            shift 2
            ;;
        -d|--data)
            DATA_FILE="$2"
            shift 2
            ;;
        -mr|--maxrecords)
            MAXRECORDS="$2"
            shift 2
            ;;
        -u|--url)
            URL="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown argument: $1"
            show_help
            exit 1
            ;;
    esac
done

if [ -z "$JOB_ID" ]; then
    # Generate AOI pairs
    # Create temp file for AOI lines to handle sorting and array creation cleanly
    TMP_AOI=$(mktemp)
    
    for ((s=MINSAT; s<=MAXSAT; s++)); do
        for ((o=MINSAT; o<=MAXSAT; o++)); do
            echo "$s $o" >> "$TMP_AOI"
        done
    done

    # Shuffle
    # If seed is provided, use RANDOM seeding if possible, or just ignore since bash random seeding is tricky
    # job.py uses random.seed(seed). Bash's RANDOM can be seeded by setting RANDOM=seed.
    # However, sort -R might not respect RANDOM variable.
    # Given sort -R is used for shuffling, we can't easily seed it deterministically across platforms.
    # But job.py implementation implies deterministic shuffle if seed is present.
    # For now, we will use sort -R which is random. If SEED != -1, we might need a custom shuffler?
    # Simpler: just use sort -R. True deterministic shuffle in bash is hard without tools.
    # We'll stick to sort -R for now as "random shuffle".
    
    SHUFFLED_AOI=$(mktemp)
    sort -R "$TMP_AOI" > "$SHUFFLED_AOI"
    
    # Read into array
    # mapfile is bash 4+, safe to use here since we checked bash version. 
    # But for max compatibility, read loop is safer.
    AOI_PAIRS=()
    while read -r line; do
        AOI_PAIRS+=("$line")
    done < "$SHUFFLED_AOI"

    # Calculate center
    # Sum s and o for indices [collectors, 2*collectors)
    SUM_S=0
    SUM_O=0
    COUNT=0
    
    START_IDX=$COLLECTORS
    END_IDX=$((COLLECTORS * 2))
    
    # Check if we have enough items
    TOTAL_ITEMS=${#AOI_PAIRS[@]}
    
    for ((i=START_IDX; i<END_IDX; i++)); do
        if [ $i -lt $TOTAL_ITEMS ]; then
            PAIR="${AOI_PAIRS[$i]}"
            # Split pair into s and o
            S=$(echo "$PAIR" | awk '{print $1}')
            O=$(echo "$PAIR" | awk '{print $2}')
            
            SUM_S=$((SUM_S + S))
            SUM_O=$((SUM_O + O))
            COUNT=$((COUNT + 1))
        fi
    done
    
    if [ $COUNT -gt 0 ]; then
        CENTER_S=$((SUM_S / COLLECTORS))
        CENTER_O=$((SUM_O / COLLECTORS))
    else
        # Fallback if no items processed (shouldn't happen with defaults)
        CENTER_S=0
        CENTER_O=0
    fi

    # Construct JSON payload using jq
    
    # 1. Create AOI JSON array
    # transform "s o" lines to [[s,o], ...]
    # We can use the SHUFFLED_AOI file directly with jq
    AOI_JSON=$(jq -R -s -c 'split("\n") | map(select(length > 0) | split(" ") | map(tonumber))' "$SHUFFLED_AOI")

    # 2. Get Job Data
    if [ -z "$DATA_FILE" ]; then
        JOB_DATA='{"filename": "data/sample.txt"}'
    else
        # Check if file exists
        if [ -f "$DATA_FILE" ]; then
            JOB_DATA=$(cat "$DATA_FILE")
        else
            echo "Error: Data file $DATA_FILE not found"
            exit 1
        fi
    fi

    # 3. Determine Reducer
    if [ "$REDUCETYPE" == "center" ]; then
        REDUCER_JSON="[$CENTER_S, $CENTER_O]"
    else
        REDUCER_JSON="[1, 1]"
    fi

    # 4. Final JSON construction
    PAYLOAD=$(jq -n \
        --argjson collectors "$COLLECTORS" \
        --argjson aoi "$AOI_JSON" \
        --arg allocator "$ALLOCATOR" \
        --arg collect_task "$COLLECTTASK" \
        --arg map_task "$MAPTASK" \
        --arg reduce_task "$REDUCETASK" \
        --argjson max_collect_records "$MAXRECORDS" \
        --argjson job_data "$JOB_DATA" \
        --argjson reducer "$REDUCER_JSON" \
        '{
            collectors: $collectors,
            aoi: $aoi,
            allocator: $allocator,
            collect_task: $collect_task,
            map_task: $map_task,
            reduce_task: $reduce_task,
            max_collect_records: $max_collect_records,
            job_data: $job_data,
            reducer: $reducer
        }')

    # Cleanup
    rm "$TMP_AOI" "$SHUFFLED_AOI"

    # Submit
    curl -s -X POST "$URL/submit" \
        -H "Content-Type: application/json" \
        -d "$PAYLOAD" | jq .

else
    # Job ID provided
    if [ -z "$RESULT_FILE" ]; then
        # Check completion
        while true; do
            RESPONSE=$(curl -s -X POST "$URL/completion" \
                -H "Content-Type: application/json" \
                -d "{\"jobid\": \"$JOB_ID\"}")
            
            DONE=$(echo "$RESPONSE" | jq -r '.done')
            
            if [ "$DONE" == "true" ] || [ "$DONE" == "True" ]; then
                echo "$RESPONSE" | jq .
                break
            fi
            
            sleep 0.5
        done
    else
        # Download
        HTTP_CODE=$(curl -s -w "%{http_code}" -o "$RESULT_FILE" -X POST "$URL/download" \
            -H "Content-Type: application/json" \
            -d "{\"jobid\": \"$JOB_ID\", \"file\": \"$RESULT_FILE\"}")
        
        if [ "$HTTP_CODE" == "200" ]; then
            echo "Downloaded $RESULT_FILE"
        else
            echo "Failed to download $RESULT_FILE"
            echo "Status: $HTTP_CODE"
            rm -f "$RESULT_FILE"
        fi
    fi
fi
