文本生成

Gemini API 可以利用 Gemini 模型，根据各种输入（包括文本、图片、视频和音频）生成文本输出。

下面是一个接受单个文本输入的基本示例：

Python
JavaScript
Go
REST
Apps 脚本

from google import genai

client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="How does AI work?"
)
print(response.text)

使用 Gemini 2.5 进行思考
2.5 Flash 和 Pro 模型默认启用了“思考”功能，以提升质量，这可能会导致运行时间延长并增加令牌用量。

使用 2.5 Flash 时，您可以通过将思考预算设置为零来停用思考功能。

如需了解详情，请参阅思考指南。

Python
JavaScript
Go
REST
Apps 脚本

from google import genai
from google.genai import types

client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="How does AI work?",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=0) # Disables thinking
    ),
)
print(response.text)
系统说明和其他配置
您可以使用系统指令来引导 Gemini 模型的行为。为此，请传递 GenerateContentConfig 对象。

Python
JavaScript
Go
REST
Apps 脚本

from google import genai
from google.genai import types

client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction="You are a cat. Your name is Neko."),
    contents="Hello there"
)

print(response.text)
借助 GenerateContentConfig 对象，您还可以替换默认生成参数，例如温度。

Python
JavaScript
Go
REST
Apps 脚本

from google import genai
from google.genai import types

client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=["Explain how AI works"],
    config=types.GenerateContentConfig(
        temperature=0.1
    )
)
print(response.text)
如需查看可配置参数及其说明的完整列表，请参阅 API 参考文档中的 GenerateContentConfig。

多模态输入
Gemini API 支持多模态输入，可让您将文本与媒体文件组合使用。以下示例演示了如何提供图片：

Python
JavaScript
Go
REST
Apps 脚本

from PIL import Image
from google import genai

client = genai.Client()

image = Image.open("/path/to/organ.png")
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[image, "Tell me about this instrument"]
)
print(response.text)
如需了解提供图片的其他方法和更高级的图片处理，请参阅我们的图片理解指南。该 API 还支持文档、视频和音频输入和理解。

流式响应
默认情况下，模型仅在整个生成过程完成后才会返回回答。

为了实现更流畅的互动，请使用流式传输在 GenerateContentResponse 实例生成时逐步接收这些实例。

Python
JavaScript
Go
REST
Apps 脚本

from google import genai

client = genai.Client()

response = client.models.generate_content_stream(
    model="gemini-2.5-flash",
    contents=["Explain how AI works"]
)
for chunk in response:
    print(chunk.text, end="")
多轮对话（聊天）
我们的 SDK 提供了将多轮提示和回复收集到聊天中的功能，让您可以轻松跟踪对话记录。

注意 ：聊天功能仅在 SDK 中实现。在后台，它仍会使用 generateContent API。对于多轮对话，系统会在每次后续对话时将完整对话记录发送给模型。
Python
JavaScript
Go
REST
Apps 脚本

from google import genai

client = genai.Client()
chat = client.chats.create(model="gemini-2.5-flash")

response = chat.send_message("I have 2 dogs in my house.")
print(response.text)

response = chat.send_message("How many paws are in my house?")
print(response.text)

for message in chat.get_history():
    print(f'role - {message.role}',end=": ")
    print(message.parts[0].text)
流式传输还可用于多轮对话。

Python
JavaScript
Go
REST
Apps 脚本

from google import genai

client = genai.Client()
chat = client.chats.create(model="gemini-2.5-flash")

response = chat.send_message_stream("I have 2 dogs in my house.")
for chunk in response:
    print(chunk.text, end="")

response = chat.send_message_stream("How many paws are in my house?")
for chunk in response:
    print(chunk.text, end="")

for message in chat.get_history():
    print(f'role - {message.role}', end=": ")
    print(message.parts[0].text)
支持的模型
Gemini 系列中的所有模型都支持文本生成。如需详细了解这些模型及其功能，请访问模型页面。

最佳做法
提示技巧
对于基本文本生成，通常只需零样本提示即可，而无需示例、系统说明或特定格式。

如需获得更贴合需求的输出，请执行以下操作：

使用系统指令来引导模型。
提供一些示例输入和输出来引导模型。这通常称为少样本提示。
如需更多提示，请参阅我们的提示工程指南。

结构化输出
在某些情况下，您可能需要结构化输出，例如 JSON。如需了解具体方法，请参阅我们的结构化输出指南。
结构化输出

您可以将 Gemini 配置为输出结构化数据，而不是非结构化文本，从而精确提取和标准化信息以供进一步处理。 例如，您可以使用结构化输出从简历中提取信息，并将其标准化以构建结构化数据库。

Gemini 可以生成 JSON 或枚举值作为结构化输出。

生成 JSON
您可以通过两种方式使用 Gemini API 生成 JSON：

在模型上配置架构
在文本提示中提供架构
在模型上配置架构是生成 JSON 的推荐方式，因为它可以限制模型输出 JSON。

配置架构（推荐）
如需限制模型生成 JSON，请配置 responseSchema。然后，模型会以 JSON 格式的输出回答任何提示。

Python
JavaScript
Go
REST

from google import genai
from pydantic import BaseModel

class Recipe(BaseModel):
    recipe_name: str
    ingredients: list[str]

client = genai.Client()
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="List a few popular cookie recipes, and include the amounts of ingredients.",
    config={
        "response_mime_type": "application/json",
        "response_schema": list[Recipe],
    },
)
# Use the response as a JSON string.
print(response.text)

# Use instantiated objects.
my_recipes: list[Recipe] = response.parsed
注意： Pydantic 验证器尚不受支持。如果发生 pydantic.ValidationError，系统会抑制该错误，并且 .parsed 可能为空/null。
输出可能如下所示：


[
  {
    "recipeName": "Chocolate Chip Cookies",
    "ingredients": [
      "1 cup (2 sticks) unsalted butter, softened",
      "3/4 cup granulated sugar",
      "3/4 cup packed brown sugar",
      "1 teaspoon vanilla extract",
      "2 large eggs",
      "2 1/4 cups all-purpose flour",
      "1 teaspoon baking soda",
      "1 teaspoon salt",
      "2 cups chocolate chips"
    ]
  },
  ...
]
在文本提示中提供架构
您可以不配置架构，而是在文本提示中以自然语言或伪代码的形式提供架构。我们不建议使用此方法，因为此方法可能会生成质量较低的输出，并且模型不受架构约束。

警告： 如果您要配置 responseSchema，请勿在文本提示中提供架构。这可能会导致结果不理想或质量不高。
下面是一个在文本提示中提供的架构的通用示例：


List a few popular cookie recipes, and include the amounts of ingredients.

Produce JSON matching this specification:

Recipe = { "recipeName": string, "ingredients": array<string> }
Return: array<Recipe>
由于模型会从提示中的文本获取架构，因此您在表示架构时可能会有一定的灵活性。但如果您像这样内联提供架构，模型实际上不受限于返回 JSON。如需获得更具确定性、更高质量的回答，请在模型上配置架构，而不要在文本提示中重复该架构。

生成枚举值
在某些情况下，您可能希望模型从选项列表中选择一个选项。如需实现此行为，您可以在架构中传递 枚举。您可以在 responseSchema 中使用枚举选项，就像使用 string 一样，因为枚举是字符串数组。与 JSON 架构类似，枚举可让您限制模型输出，以满足应用的要求。

例如，假设您正在开发一个应用，用于将乐器分为五类："Percussion"、"String"、"Woodwind"、"Brass" 或“"Keyboard"”。您可以创建一个枚举来帮助完成此任务。

在以下示例中，您传递了一个枚举作为 responseSchema，从而限制模型选择最合适的选项。

Python
JavaScript
REST

from google import genai
import enum

class Instrument(enum.Enum):
  PERCUSSION = "Percussion"
  STRING = "String"
  WOODWIND = "Woodwind"
  BRASS = "Brass"
  KEYBOARD = "Keyboard"

client = genai.Client()
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What type of instrument is an oboe?',
    config={
        'response_mime_type': 'text/x.enum',
        'response_schema': Instrument,
    },
)

print(response.text)
# Woodwind
Python 库将转换 API 的类型声明。不过，该 API 接受 OpenAPI 3.0 架构 (Schema) 的子集。

还有两种其他方式可以指定枚举。您可以使用 Literal： ```

Python

Literal["Percussion", "String", "Woodwind", "Brass", "Keyboard"]
您还可以将架构作为 JSON 传递：

Python

from google import genai

client = genai.Client()
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What type of instrument is an oboe?',
    config={
        'response_mime_type': 'text/x.enum',
        'response_schema': {
            "type": "STRING",
            "enum": ["Percussion", "String", "Woodwind", "Brass", "Keyboard"],
        },
    },
)

print(response.text)
# Woodwind
除了基本的多项选择题之外，您还可以在 JSON 架构中的任何位置使用枚举。例如，您可以让模型提供食谱标题列表，并使用 Grade 枚举为每个标题指定热度等级：

Python

from google import genai

import enum
from pydantic import BaseModel

class Grade(enum.Enum):
    A_PLUS = "a+"
    A = "a"
    B = "b"
    C = "c"
    D = "d"
    F = "f"

class Recipe(BaseModel):
  recipe_name: str
  rating: Grade

client = genai.Client()
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='List 10 home-baked cookie recipes and give them grades based on tastiness.',
    config={
        'response_mime_type': 'application/json',
        'response_schema': list[Recipe],
    },
)

print(response.text)
响应可能如下所示：


[
  {
    "recipe_name": "Chocolate Chip Cookies",
    "rating": "a+"
  },
  {
    "recipe_name": "Peanut Butter Cookies",
    "rating": "a"
  },
  {
    "recipe_name": "Oatmeal Raisin Cookies",
    "rating": "b"
  },
  ...
]
JSON 架构简介
使用 responseSchema 参数将模型配置为 JSON 输出时，需要依赖 Schema 对象来定义其结构。此对象表示 OpenAPI 3.0 架构对象的选定子集，并添加了 propertyOrdering 字段。

提示： 在 Python 中，当您使用 Pydantic 模型时，无需直接处理 Schema 对象，因为该对象会自动转换为相应的 JSON 架构。如需了解详情，请参阅 Python 中的 JSON 架构。
以下是所有 Schema 字段的伪 JSON 表示法：


{
  "type": enum (Type),
  "format": string,
  "description": string,
  "nullable": boolean,
  "enum": [
    string
  ],
  "maxItems": integer,
  "minItems": integer,
  "properties": {
    string: {
      object (Schema)
    },
    ...
  },
  "required": [
    string
  ],
  "propertyOrdering": [
    string
  ],
  "items": {
    object (Schema)
  }
}
架构的 Type 必须是 OpenAPI 数据类型之一，或这些类型的并集（使用 anyOf）。每个 Type 仅有一部分字段有效。下表将每个 Type 映射到适用于相应类型的字段子集：

string -> enum、format、nullable
integer -> format、minimum、maximum、enum、nullable
number -> format、minimum、maximum、enum、nullable
boolean -> nullable
array -> minItems、maxItems、items、nullable
object -> properties、required、propertyOrdering、nullable
以下是一些示例架构，展示了有效的类型和字段组合：


{ "type": "string", "enum": ["a", "b", "c"] }

{ "type": "string", "format": "date-time" }

{ "type": "integer", "format": "int64" }

{ "type": "number", "format": "double" }

{ "type": "boolean" }

{ "type": "array", "minItems": 3, "maxItems": 3, "items": { "type": ... } }

{ "type": "object",
  "properties": {
    "a": { "type": ... },
    "b": { "type": ... },
    "c": { "type": ... }
  },
  "nullable": true,
  "required": ["c"],
  "propertyOrdering": ["c", "b", "a"]
}
如需查看 Gemini API 中使用的架构字段的完整文档，请参阅架构参考。

媒体资源排序
警告： 配置 JSON 架构时，请务必设置 propertyOrdering[]；提供示例时，请确保示例中的属性顺序与架构一致。
在 Gemini API 中使用 JSON 架构时，属性的顺序非常重要。默认情况下，该 API 会按字母顺序对属性进行排序，并且不会保留属性的定义顺序（不过 Google Gen AI SDK 可能会保留此顺序）。如果您向配置了架构的模型提供示例，但示例的属性顺序与架构的属性顺序不一致，则输出可能会杂乱无章或出乎意料。

为确保属性的顺序一致且可预测，您可以使用可选的 propertyOrdering[] 字段。


"propertyOrdering": ["recipeName", "ingredients"]
propertyOrdering[]（并非 OpenAPI 规范中的标准字段）是一个字符串数组，用于确定响应中属性的顺序。通过指定属性的顺序，然后提供具有相同属性顺序的示例，您有望提高结果的质量。仅当您手动创建 types.Schema 时，系统才支持 propertyOrdering。

Python 中的架构
使用 Python 库时，response_schema 的值必须是以下值之一：

一种类型，与您在类型注释中使用的类型相同（请参阅 Python typing 模块）
genai.types.Schema 的实例
genai.types.Schema 的 dict 等效项
定义架构的最简单方法是使用 Pydantic 类型（如上一个示例所示）：

Python

config={'response_mime_type': 'application/json',
        'response_schema': list[Recipe]}
当您使用 Pydantic 类型时，Python 库会为您构建 JSON 架构并将其发送到 API。如需查看更多示例，请参阅 Python 库文档。

Python 库支持使用以下类型定义的架构（其中 AllowedType 是任何允许的类型）：

int
float
bool
str
list[AllowedType]
AllowedType|AllowedType|...
对于结构化类型：
dict[str, AllowedType]。此注释声明所有字典值都应为同一类型，但未指定应包含哪些键。
用户定义的 Pydantic 模型。这种方法可让您指定键名，并为与每个键关联的值定义不同的类型，包括嵌套结构。
JSON 架构支持
JSON 架构是比 OpenAPI 3.0 更新的规范，Schema 对象基于该规范。JSON 架构支持以预览版形式提供，通过字段 responseJsonSchema 实现，该字段接受任何 JSON 架构，但有以下限制：

它仅适用于 Gemini 2.5。
虽然可以传递所有 JSON 架构属性，但并非所有属性都受支持。如需了解详情，请参阅相应字段的文档。
递归引用只能用作非必需对象属性的值。
递归引用会根据架构的大小展开到有限的程度。
包含 $ref 的架构不能包含以 $ 开头以外的任何属性。
以下示例展示了如何使用 Pydantic 生成 JSON 架构并将其提交给模型：


curl "https://generativelanguage.googleapis.com/v1alpha/models/\
gemini-2.5-flash:generateContent" \
    -H "x-goog-api-key: $GEMINI_API_KEY"\
    -H 'Content-Type: application/json' \
    -d @- <<EOF
{
  "contents": [{
    "parts":[{
      "text": "Please give a random example following this schema"
    }]
  }],
  "generationConfig": {
    "response_mime_type": "application/json",
    "response_json_schema": $(python3 - << PYEOF
    from enum import Enum
    from typing import List, Optional, Union, Set
    from pydantic import BaseModel, Field, ConfigDict
    import json

    class UserRole(str, Enum):
        ADMIN = "admin"
        VIEWER = "viewer"

    class Address(BaseModel):
        street: str
        city: str

    class UserProfile(BaseModel):
        username: str = Field(description="User's unique name")
        age: Optional[int] = Field(ge=0, le=120)
        roles: Set[UserRole] = Field(min_items=1)
        contact: Union[Address, str]
        model_config = ConfigDict(title="User Schema")

    # Generate and print the JSON Schema
    print(json.dumps(UserProfile.model_json_schema(), indent=2))
    PYEOF
    )
  }
}
EOF
使用 SDK 时，尚不支持直接传递 JSON 架构。

最佳做法
使用响应架构时，请谨记以下注意事项和最佳实践：

回答架构的大小会计入输入 token 限制。
默认情况下，字段是可选的，这意味着模型可以填充字段或跳过字段。您可以将字段设置为必填字段，以强制模型提供值。如果关联的输入提示中上下文不足，模型会主要基于其训练所依据的数据生成回答。
复杂的架构可能会导致 InvalidArgument: 400 错误。复杂性可能来自属性名称过长、数组长度限制过长、枚举值过多、对象具有许多可选属性，或者是这些因素的组合。

如果您在使用有效架构时看到此错误，请进行以下一项或多项更改以解决此错误：

缩短属性名称或枚举名称。
展平嵌套数组。
减少存在限制的属性的数量，例如具有下限和上限的数量。
减少存在复杂限制的属性的数量，例如采用 date-time 等复杂格式的属性。
减少可选属性的数量。
减少枚举的有效值数量。
如果您未看到预期结果，请在输入提示中添加更多上下文或修改响应架构。例如，查看非结构化输出情况下模型的响应，以了解模型的响应方式。然后，您可以更新响应架构，使其更贴合模型的输出。如需查看有关结构化输出的其他问题排查提示，请参阅问题排查指南。
生成内容时进行思考
使用思考模型发起请求与发起任何其他内容生成请求类似。主要区别在于，您需要在 model 字段中指定支持思考的模型，如以下文本生成示例所示：

Python
JavaScript
Go
REST

from google import genai

client = genai.Client()
prompt = "Explain the concept of Occam's Razor and provide a simple, everyday example."
response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents=prompt
)

print(response.text)
思考预算
thinkingBudget 参数可指导模型了解在生成回答时要使用的思考 token 数量。一般来说，token 数量越多，推理就越细致，这有助于处理更复杂的任务。如果延迟时间更重要，请使用较低的预算，或通过将 thinkingBudget 设置为 0 来停用思考。将 thinkingBudget 设置为 -1 会开启动态思考，这意味着模型会根据请求的复杂程度调整预算。

thinkingBudget 仅在 Gemini 2.5 Flash、2.5 Pro 和 2.5 Flash-Lite 中受支持。根据提示的不同，模型可能会超出或未达到令牌预算。

以下是每种模型类型的 thinkingBudget 配置详细信息。

型号	默认设置
（未设置思考预算）	Range	停用思考	开启动态思维
2.5 Pro	动态思考：模型决定何时思考以及思考多少	128到32768	不适用：无法停用思考	thinkingBudget = -1
2.5 Flash	动态思考：模型决定何时思考以及思考多少	0到24576	thinkingBudget = 0	thinkingBudget = -1
2.5 Flash Lite	模型不思考	512到24576	thinkingBudget = 0	thinkingBudget = -1
Python
JavaScript
Go
REST

from google import genai
from google.genai import types

client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents="Provide a list of 3 famous physicists and their key contributions",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=1024)
        # Turn off thinking:
        # thinking_config=types.ThinkingConfig(thinking_budget=0)
        # Turn on dynamic thinking:
        # thinking_config=types.ThinkingConfig(thinking_budget=-1)
    ),
)

print(response.text)
想法总结
想法摘要是模型原始想法的合成版本，可帮助您深入了解模型的内部推理过程。请注意，思考预算适用于模型的原始想法，而不适用于想法摘要。

您可以在请求配置中将 includeThoughts 设置为 true，以启用思路总结。然后，您可以通过迭代 response 参数的 parts 并检查 thought 布尔值来访问摘要。

以下示例展示了如何在不进行流式传输的情况下启用和检索思路总结，该方法会在响应中返回单个最终思路总结：

Python
JavaScript
Go

from google import genai
from google.genai import types

client = genai.Client()
prompt = "What is the sum of the first 50 prime numbers?"
response = client.models.generate_content(
  model="gemini-2.5-pro",
  contents=prompt,
  config=types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(
      include_thoughts=True
    )
  )
)

for part in response.candidates[0].content.parts:
  if not part.text:
    continue
  if part.thought:
    print("Thought summary:")
    print(part.text)
    print()
  else:
    print("Answer:")
    print(part.text)
    print()

以下示例展示了如何使用流式思考，该功能可在生成期间返回滚动式增量摘要：

Python
JavaScript
Go

from google import genai
from google.genai import types

client = genai.Client()

prompt = """
Alice, Bob, and Carol each live in a different house on the same street: red, green, and blue.
The person who lives in the red house owns a cat.
Bob does not live in the green house.
Carol owns a dog.
The green house is to the left of the red house.
Alice does not own a cat.
Who lives in each house, and what pet do they own?
"""

thoughts = ""
answer = ""

for chunk in client.models.generate_content_stream(
    model="gemini-2.5-pro",
    contents=prompt,
    config=types.GenerateContentConfig(
      thinking_config=types.ThinkingConfig(
        include_thoughts=True
      )
    )
):
  for part in chunk.candidates[0].content.parts:
    if not part.text:
      continue
    elif part.thought:
      if not thoughts:
        print("Thoughts summary:")
      print(part.text)
      thoughts += part.text
    else:
      if not answer:
        print("Answer:")
      print(part.text)
      answer += part.text
思想签名
由于标准 Gemini API 文本和内容生成调用是无状态的，因此在多轮互动（例如聊天）中使用思考时，模型无法访问之前轮次的思考上下文。

您可以使用思维签名来保持思维上下文，思维签名是模型内部思维过程的加密表示形式。启用思考和函数调用后，模型会在响应对象中返回思考签名。为确保模型在对话的多个轮次中保持上下文，您必须在后续请求中将思路签名提供给模型。

在以下情况下，您会收到想法签名：

已启用思考功能，并生成了想法。
请求包含函数声明。
注意： 只有在使用函数调用时，系统才会提供思路签名；具体来说，您的请求必须包含函数声明。
您可以在函数调用页面上找到使用函数调用进行思考的示例。

使用函数调用时，还需考虑以下用量限制：

签名由模型在响应的其他部分（例如函数调用或文本部分）中返回。在后续对话轮次中，将包含所有部分的完整回答返回给模型。
请勿将带有签名的部分串联在一起。
请勿将已签名的部分与未签名的部分合并。
价格
注意： 摘要在 API 的免费层级和付费层级中均可用。思考签名会增加作为请求的一部分发送回时所收取的输入令牌费用。
开启思考功能后，回答价格是输出 token 和思考 token 的总和。您可以从 thoughtsTokenCount 字段获取生成的思考令牌总数。

Python
JavaScript
Go

# ...
print("Thoughts tokens:",response.usage_metadata.thoughts_token_count)
print("Output tokens:",response.usage_metadata.candidates_token_count)
思考模型会生成完整的想法，以提高最终回答的质量，然后输出摘要，以便深入了解思考过程。因此，价格取决于模型生成摘要所需的完整思维令牌数量，尽管 API 仅输出摘要。

如需详细了解令牌，请参阅令牌计数指南。

支持的模型
所有 2.5 系列型号均支持思考功能。您可以在模型概览页面上找到所有模型功能。

最佳做法
本部分包含一些有关如何高效使用思维模型的指导。 与往常一样，遵循我们的提示指南和最佳实践将有助于您获得最佳结果。

调试和指导
检查推理过程：当推理模型未给出您预期的回答时，仔细分析 Gemini 的推理总结会有所帮助。您可以了解模型如何分解任务并得出结论，并使用该信息来修正结果，使其更符合预期。

在推理中提供指导：如果您希望获得特别长的输出，不妨在提示中提供指导，以限制模型使用的思考量。这样一来，您就可以为回答预留更多令牌输出。

任务复杂程度
简单任务（无需思考）：对于不需要复杂推理的简单请求（例如事实检索或分类），无需思考。例如：
“DeepMind 是在哪里成立的？”
“这封电子邮件是要求安排会议，还是仅提供信息？”
中等任务（默认/需要一定程度的思考）：许多常见请求都需要一定程度的分步处理或更深入的理解。Gemini 可以灵活运用思考能力来处理以下任务：
将光合作用和成长进行类比。
比较并对比电动汽车和混合动力汽车。
困难任务（最大思维能力）：对于真正复杂的挑战，例如解决复杂的数学问题或编码任务，我们建议设置较高的思维预算。这类任务要求模型充分发挥推理和规划能力，通常需要经过许多内部步骤才能提供答案。例如：
解决 2025 年 AIME 中的问题 1：求出所有整数基数 b > 9 的和，使得 17b 是 97b 的除数。
为可直观呈现实时股票市场数据的 Web 应用编写 Python 代码，包括用户身份验证。尽可能提高效率。
利用工具和功能进行思考
思考模型可与 Gemini 的所有工具和功能搭配使用。这使模型能够与外部系统互动、执行代码或访问实时信息，并将结果纳入其推理和最终回答中。

借助搜索工具，模型可以查询 Google 搜索，以查找最新信息或超出其训练数据范围的信息。这对于询问近期发生的事件或高度具体的主题非常有用。

借助代码执行工具，模型可以生成并运行 Python 代码，以执行计算、处理数据或解决最适合通过算法处理的问题。模型会接收代码的输出，并可在回答中使用该输出。

借助结构化输出，您可以限制 Gemini 以 JSON 格式进行回答。这对于将模型的输出集成到应用中特别有用。

函数调用将思维模型连接到外部工具和 API，因此它可以推理出何时调用正确的函数以及要提供哪些参数。

网址上下文可为模型提供网址，作为提示的额外上下文。然后，模型可以从网址中检索内容，并使用该内容来提供和调整回答。

您可以在思维食谱中查看将工具与思维模型搭配使用的示例。
