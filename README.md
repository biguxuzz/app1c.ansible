# Установка Postgres Pro 1C и платформы 1С

Этот проект содержит Ansible playbook для автоматизации установки Postgres Pro 1C и платформы 1С на Ubuntu 22.04.

## Структура проекта

```
.
├── ansible.cfg
├── inventory
├── group_vars
│   └── all.yml
├── roles
│   ├── postgres
│   │   ├── defaults
│   │   │   └── main.yml
│   │   └── tasks
│   │       └── main.yml
│   └── one_c_server
│       ├── defaults
│       │   └── main.yml
│       ├── tasks
│       │   └── main.yml
│       └── templates
│           ├── ras.override.conf.j2
│           └── srv1cv8.override.conf.j2
└── site.yml
```

## Предварительные требования

- Ubuntu 22.04
- Ansible

## Настройка

1. Отредактируйте файл `inventory`, если необходимо изменить конфигурацию локального хоста:
```ini
[postgres]
postgres_host ansible_host=your_postgres_host ansible_connection=ssh

[one_c_server]
1c_host ansible_host=your_1c_host ansible_connection=ssh
```

2. При необходимости измените параметры в файлах:
   - `roles/postgres/defaults/main.yml` - параметры PostgreSQL
   - `roles/one_c_server/defaults/main.yml` - параметры сервера 1С
   - `group_vars/all.yml` - общие параметры

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/biguxuzz/app1c.ansible.git
   cd app1c.ansible
   ```

2. Запустите playbook:
   ```bash
   ansible-playbook site.yml --ask-become-pass
   ```

## Что устанавливается

- Postgres Pro 1C 17
- Платформа 1С 8.3.26.1521

## Проверка установки

После установки вы можете проверить статус служб:

```bash
systemctl status postgresql
systemctl status srv1cv8-8.3.26.1521@debug_1540
systemctl status ras-8.3.26.1521@debug_1540
```

## Активация лицензии сообщества

Для активации лицензии сообщества 1С:

1. Создайте новую базу данных
2. Убедитесь, что файл лицензии принадлежит пользователю `usr1cv8`

## Настройка

Вы можете изменить параметры установки в файле `group_vars/all.yml`.

## Примеры запуска

### Установка только 1С с измененными портами

Для установки только сервера 1С с измененными портами используйте следующую команду:

```bash
ansible-playbook site.yml --limit one_c_server -e "ragent_port=1740 rmngr_port=1741 rphost_start_port=1760 rphost_end_port=1791 ras_port=1745" --ask-become-pass
```

Эта команда:
- Устанавливает только сервер 1С (пропускает установку PostgreSQL)
- Устанавливает порт `ragent` на 1740
- Устанавливает порт `rmngr` на 1741
- Устанавливает диапазон портов `rphost` на 1760-1791
- Устанавливает порт `ras` на 1745
- Запрашивает пароль для повышения привилегий (sudo)

### Установка только PostgreSQL

Для установки только PostgreSQL используйте следующую команду:

```bash
ansible-playbook site.yml --limit postgres --ask-become-pass
```

## Лицензия

Этот проект распространяется под лицензией GNU General Public License версии 3 (GPL-3.0). Полный текст лицензии доступен в файле LICENSE в корневой директории проекта. 