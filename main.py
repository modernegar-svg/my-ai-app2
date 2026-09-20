import flet as ft
from openai import OpenAI

API_KEY = "sk-apx2f4ff3acbee2c6087886a4d8866f37d20b7b284600b1aa2"
BASE_URL = "https://api.apinex.bond/v1"

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
)

chat_history = [
    {
        "role": "system",
        "content": "Ты дружелюбный и умный AI-помощник. Отвечай красиво, четко и структурировано.",
    }
]


def main(page: ft.Page):
    try:
        page.title = "AI Assistant"
        page.theme_mode = ft.ThemeMode.DARK
        page.padding = 15

        chat_list = ft.ListView(
            expand=True, spacing=12, padding=10, auto_scroll=True
        )

        user_input = ft.TextField(
            hint_text="Задайте вопрос...",
            multiline=True,
            min_lines=1,
            max_lines=3,
            expand=True,
            border_radius=20,
            content_padding=12,
        )

        loading = ft.ProgressBar(visible=False, color="blue400")

        def copy_to_clipboard(text_to_copy: str):
            page.set_clipboard(text_to_copy)
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Скопировано в буфер обмена!"), duration=1500
            )
            page.snack_bar.open = True
            page.update()

        def add_message(role_name: str, text: str, is_user: bool):
            avatar_icon = "person" if is_user else "smart_toy"
            avatar_bg = "blue700" if is_user else "green700"
            bubble_bg = "blueGrey900" if is_user else "surfaceVariant"
            align = (
                ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START
            )

            actions = []
            if not is_user:
                actions = [
                    ft.Row(
                        [
                            ft.IconButton(
                                icon="content_copy_rounded",
                                icon_size=16,
                                tooltip="Скопировать",
                                on_click=lambda e: copy_to_clipboard(text),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.END,
                        spacing=0,
                    )
                ]

            chat_list.controls.append(
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.CircleAvatar(
                                                content=ft.Icon(
                                                    avatar_icon, size=16
                                                ),
                                                bgcolor=avatar_bg,
                                                radius=12,
                                            ),
                                            ft.Text(
                                                role_name,
                                                weight=ft.FontWeight.BOLD,
                                                size=12,
                                                color="grey400",
                                            ),
                                        ],
                                        spacing=8,
                                    ),
                                    ft.Markdown(
                                        value=text,
                                        selectable=True,
                                        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                                    ),
                                    *actions,
                                ],
                                tight=True,
                            ),
                            bgcolor=bubble_bg,
                            padding=12,
                            border_radius=15,
                            width=320,
                        )
                    ],
                    alignment=align,
                )
            )
            page.update()

        add_message(
            "AI Помощник", "Привет! Чем могу помочь сегодня?", is_user=False
        )

        def send_prompt(prompt_prefix=""):
            user_text = user_input.value.strip()
            if not user_text and not prompt_prefix:
                return

            final_user_text = (
                f"{prompt_prefix}\n\n{user_text}" if prompt_prefix else user_text
            )
            user_input.value = ""

            add_message("Вы", final_user_text, is_user=True)
            chat_history.append({"role": "user", "content": final_user_text})

            loading.visible = True
            page.update()

            try:
                recent_history = [chat_history[0]] + chat_history[-10:]
                response = client.chat.completions.create(
                    messages=recent_history, model="free/kimi-k3"
                )
                bot_reply = response.choices[0].message.content
                chat_history.append({"role": "assistant", "content": bot_reply})
                add_message("AI Помощник", bot_reply, is_user=False)
            except Exception as err:
                add_message("Ошибка сети/API", f"`{str(err)}`", is_user=False)

            loading.visible = False
            page.update()

        def clear_chat(e):
            global chat_history
            chat_history = [chat_history[0]]
            chat_list.controls.clear()
            add_message("Система", "Память диалога очищена!", is_user=False)

        header = ft.Container(
            content=ft.Row(
                [
                    ft.Row(
                        [
                            ft.Icon("auto_awesome", color="blue400"),
                            ft.Text(
                                "AI Assistant",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ]
                    ),
                    ft.IconButton(
                        icon="delete_outline",
                        icon_color="grey400",
                        on_click=clear_chat,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.only(bottom=5),
        )

        input_row = ft.Row(
            [
                user_input,
                ft.IconButton(
                    icon="send_rounded",
                    icon_color="blue400",
                    icon_size=28,
                    on_click=lambda e: send_prompt(),
                ),
            ]
        )

        page.add(header, ft.Divider(height=1), chat_list, loading, input_row)

    except Exception as e:
        # Если приложение падает при старте, покажем ошибку прямо на экране белого листа
        page.add(
            ft.Text(f"Критическая ошибка запуска: {e}", color="red", size=16)
        )
        page.update()


if __name__ == "__main__":
    if hasattr(ft, "app"):
        ft.app(target=main)
