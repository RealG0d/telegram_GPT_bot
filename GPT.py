from openai import AsyncOpenAI
import sqlite3

client = AsyncOpenAI(api_key='YOUR_KEY')


async def gpt(text: str, user_id: int) -> str | bool:
    try:
        connect = sqlite3.connect("gpt_us.db", check_same_thread=False)
        cursor = connect.cursor()
        result = cursor.execute("SELECT con, con2, personality FROM ChatGPT WHERE id = ?", (user_id,)).fetchone()
        if result:
            con, con2, person = result
        else:
            con, con2, person = "", "", ""

        completion = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"{person}"},
                {"role": "user", "content": f"{text}"},
                {"role": "assistant", "content": f"{con} {con2}"}
            ],
            temperature=0.9
        )

        english_text = completion.choices[0].message.content

        try:
            cursor.execute(
                "UPDATE ChatGPT SET con = ?, con2 = ? WHERE id = ?",
                (con, english_text, user_id)
            )
        except sqlite3.OperationalError:
            cursor.execute(
                "UPDATE ChatGPT SET con = ?, con2 = ? WHERE id = ?",
                (con, "", user_id)
            )
        connect.commit()
        connect.close()

        return english_text
    except Exception as ex:
        print(ex)
        return False