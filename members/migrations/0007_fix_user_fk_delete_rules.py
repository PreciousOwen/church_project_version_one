from django.db import migrations


def apply_user_fk_delete_rules(apps, schema_editor):
    if schema_editor.connection.vendor != "mysql":
        return

    foreign_keys = [
        ("auth_user_groups", "auth_user_groups_user_id_6a12ed8b_fk_auth_user_id", "user_id", "CASCADE"),
        ("auth_user_user_permissions", "auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id", "user_id", "CASCADE"),
        ("django_admin_log", "django_admin_log_user_id_c564eba6_fk_auth_user_id", "user_id", "CASCADE"),
        ("members_memberapplication", "members_memberapplication_user_id_8532eb4e_fk_auth_user_id", "user_id", "CASCADE"),
        ("members_memberapplication", "members_memberapplic_reviewed_by_id_34672d06_fk_auth_user", "reviewed_by_id", "SET NULL"),
    ]

    with schema_editor.connection.cursor() as cursor:
        for table_name, constraint_name, column_name, delete_rule in foreign_keys:
            cursor.execute(
                """
                SELECT rc.DELETE_RULE
                FROM information_schema.REFERENTIAL_CONSTRAINTS rc
                WHERE rc.CONSTRAINT_SCHEMA = DATABASE()
                  AND rc.CONSTRAINT_NAME = %s
                  AND rc.TABLE_NAME = %s
                """,
                [constraint_name, table_name],
            )
            row = cursor.fetchone()
            if row and row[0] == delete_rule:
                continue

            cursor.execute(f"ALTER TABLE `{table_name}` DROP FOREIGN KEY `{constraint_name}`")
            cursor.execute(
                f"""
                ALTER TABLE `{table_name}`
                ADD CONSTRAINT `{constraint_name}`
                FOREIGN KEY (`{column_name}`) REFERENCES `auth_user` (`id`) ON DELETE {delete_rule}
                """
            )


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0006_memberapplication"),
    ]

    operations = [
        migrations.RunPython(apply_user_fk_delete_rules, migrations.RunPython.noop),
    ]
