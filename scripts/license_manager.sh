#!/bin/bash

# Пути к исполняемым файлам и директориям
RING_PATH="/opt/1C/1CE/components/1c-enterprise-ring-0.19.5+12-x86_64"
LICENSE_PATH="/mnt/e/temp/lic/gst"
OUTPUT_DIR="$HOME/license_requests"
SCRIPTS_DIR="$OUTPUT_DIR/scripts"

# Создаем директории для выходных файлов, если их нет
mkdir -p "$OUTPUT_DIR"
mkdir -p "$SCRIPTS_DIR"

# Функция для получения списка лицензий
get_license_list() {
    local output
    output=$("$RING_PATH/ring" license list --path "$LICENSE_PATH")
    echo "$output" | grep -E '^[0-9]+-[0-9]+' | awk '{print $1}'
}

# Функция для получения информации о лицензии
get_license_info() {
    local license_name=$1
    "$RING_PATH/ring" license info --path "$LICENSE_PATH" --name "$license_name"
}

# Функция для извлечения значения из информации о лицензии
extract_value() {
    local info=$1
    local field=$2
    echo "$info" | grep -A 1000 "$field:" | grep -m 1 -v "^$field:" | sed 's/^[[:space:]]*//' | sed "s/^$field: //"
}

# Функция для создания скрипта запроса на лицензию
create_license_script() {
    local license_name=$1
    local info=$2
    local script_file="$SCRIPTS_DIR/request_$license_name.sh"
    local log_file="$OUTPUT_DIR/log_$license_name.txt"

    # Извлекаем данные из информации о лицензии
    local company=$(extract_value "$info" "Компания")
    local last_name=$(extract_value "$info" "Фамилия")
    local first_name=$(extract_value "$info" "Имя")
    local middle_name=$(extract_value "$info" "Отчество")
    local email=$(extract_value "$info" "e-mail")
    local country=$(extract_value "$info" "Страна")
    local zip_code=$(extract_value "$info" "Индекс")
    local town=$(extract_value "$info" "Город")
    local street=$(extract_value "$info" "Улица")
    local house=$(extract_value "$info" "Дом")
    local building=$(extract_value "$info" "Корпус")
    local apartment=$(extract_value "$info" "Квартира/офис")
    local serial=$(echo "$info" | grep "Регистрационный номер:" | awk '{print $3}' | sed 's/G0$//')
    local pin=$(echo "$license_name" | cut -d'-' -f1)

    # Создаем скрипт для запроса лицензии
    cat > "$script_file" << EOF
#!/bin/bash

# Скрипт для запроса лицензии $license_name
# Создан автоматически. При необходимости отредактируйте параметры.

RING_PATH="$RING_PATH"
REQUEST_FILE="$OUTPUT_DIR/request_$license_name.txt"
LOG_FILE="$log_file"

# Выполнение запроса на лицензию
"\$RING_PATH/ring" license prepare-request \\
    --serial "$serial" \\
    --previous-pin "$pin" \\
    --pin "$pin" \\
    --company "\"$company\"" \\
    --last-name "$last_name" \\
    --first-name "$first_name" \\
    --middle-name "$middle_name" \\
    --email "$email" \\
    --country "$country" \\
    --zip-code "$zip_code" \\
    --region "Область" \\
    --town "$town" \\
    --street "$street" \\
    --house "$house" \\
    --building "$building" \\
    --apartment "$apartment" \\
    --request "\$REQUEST_FILE" > "\$LOG_FILE" 2>&1

if [ \$? -eq 0 ]; then
    echo "Запрос успешно создан: \$REQUEST_FILE"
else
    echo "Ошибка при создании запроса"
    cat "\$LOG_FILE"
fi
EOF

    # Делаем скрипт исполняемым
    chmod +x "$script_file"
    echo "Создан скрипт для лицензии $license_name: $script_file"
}

# Основной цикл обработки лицензий
echo "Поиск лицензий..."
licenses=$(get_license_list)
echo "Найдено лицензий: $(echo "$licenses" | wc -l)"

while IFS= read -r license_name; do
    if [ -z "$license_name" ]; then
        continue
    fi

    echo "Обработка лицензии: $license_name"
    license_info=$(get_license_info "$license_name")
    create_license_script "$license_name" "$license_info"
done <<< "$licenses"

echo "Обработка завершена"
echo "Скрипты для запросов лицензий созданы в директории: $SCRIPTS_DIR"
echo "Для выполнения запроса на лицензию запустите соответствующий скрипт из этой директории" 