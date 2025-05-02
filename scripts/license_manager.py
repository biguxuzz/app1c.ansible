#!/usr/bin/env python3
import subprocess
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional

class LicenseManager:
    def __init__(self, ring_path: str, license_path: str):
        self.ring_path = ring_path
        self.license_path = license_path

    def _run_command(self, command: List[str]) -> str:
        """Выполняет команду и возвращает её вывод"""
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout

    def get_license_list(self) -> List[str]:
        """Получает список лицензий из указанной директории"""
        command = [
            f"{self.ring_path}/ring",
            "license",
            "list",
            "--path",
            self.license_path
        ]
        output = self._run_command(command)
        licenses = []
        for line in output.split('\n'):
            if line.strip() and not line.startswith('WARNING'):
                match = re.match(r'(\d+-\d+)', line)
                if match:
                    licenses.append(match.group(1))
        return licenses

    def get_license_info(self, license_name: str) -> Dict:
        """Получает информацию о конкретной лицензии"""
        command = [
            f"{self.ring_path}/ring",
            "license",
            "info",
            "--path",
            self.license_path,
            "--name",
            license_name
        ]
        output = self._run_command(command)
        
        info = {}
        current_section = None
        
        for line in output.split('\n'):
            if line.startswith('WARNING'):
                continue
                
            if ':' in line and not line.startswith('    '):
                current_section = line.split(':')[0].strip()
                info[current_section] = {}
            elif line.strip() and current_section:
                if ':' in line:
                    key, value = line.split(':', 1)
                    info[current_section][key.strip()] = value.strip()
        
        return info

    def prepare_license_request(
        self,
        serial: str,
        previous_pin: str,
        pin: str,
        company: str,
        last_name: str,
        first_name: str,
        middle_name: str,
        email: str,
        country: str,
        zip_code: str,
        region: str,
        town: str,
        street: str,
        house: str,
        building: str,
        apartment: str,
        request_file: str
    ) -> None:
        """Подготавливает запрос на лицензию"""
        command = [
            f"{self.ring_path}/ring",
            "license",
            "prepare-request",
            "--serial", serial,
            "--previous-pin", previous_pin,
            "--pin", pin,
            "--company", company,
            "--last-name", last_name,
            "--first-name", first_name,
            "--middle-name", middle_name,
            "--email", email,
            "--country", country,
            "--zip-code", zip_code,
            "--region", region,
            "--town", town,
            "--street", street,
            "--house", house,
            "--building", building,
            "--apartment", apartment,
            "--request", request_file
        ]
        
        self._run_command(command)

def main():
    # Пути к исполняемым файлам и директориям
    RING_PATH = "/opt/1C/1CE/components/1c-enterprise-ring-0.19.5+12-x86_64"
    LICENSE_PATH = "/mnt/e/temp/lic/gst"
    OUTPUT_DIR = os.path.expanduser("~/license_requests")
    
    # Создаем директорию для выходных файлов, если её нет
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    
    # Инициализируем менеджер лицензий
    manager = LicenseManager(RING_PATH, LICENSE_PATH)
    
    # Получаем список лицензий
    licenses = manager.get_license_list()
    print(f"Найдено лицензий: {len(licenses)}")
    
    # Обрабатываем каждую лицензию
    for license_name in licenses:
        print(f"\nОбработка лицензии: {license_name}")
        
        # Получаем информацию о лицензии
        info = manager.get_license_info(license_name)
        
        # Извлекаем необходимые данные
        user_info = info.get('Информация о пользователе', {})
        product_info = info.get('Информация о продукте', {})
        
        # Подготавливаем запрос
        request_file = os.path.join(OUTPUT_DIR, f"request_{license_name}.txt")
        log_file = os.path.join(OUTPUT_DIR, f"log_{license_name}.txt")
        
        try:
            manager.prepare_license_request(
                serial=product_info.get('Регистрационный номер', '').replace('G0', ''),
                previous_pin=license_name.split('-')[0],
                pin=license_name.split('-')[0],
                company=f'"{user_info.get("Компания", "")}"',
                last_name=user_info.get('Фамилия', ''),
                first_name=user_info.get('Имя', ''),
                middle_name=user_info.get('Отчество', ''),
                email=user_info.get('e-mail', ''),
                country=user_info.get('Страна', ''),
                zip_code=user_info.get('Индекс', ''),
                region='Область',
                town=user_info.get('Город', ''),
                street=user_info.get('Улица', ''),
                house=user_info.get('Дом', ''),
                building=user_info.get('Корпус', ''),
                apartment=user_info.get('Квартира/офис', ''),
                request_file=request_file
            )
            
            print(f"Запрос успешно создан: {request_file}")
            
        except Exception as e:
            print(f"Ошибка при обработке лицензии {license_name}: {str(e)}")
            with open(log_file, 'w') as f:
                f.write(f"Ошибка: {str(e)}\n")

if __name__ == "__main__":
    main() 