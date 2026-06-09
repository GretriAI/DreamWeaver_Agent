import os
import json
import uuid
from openai import OpenAI

class SyntheticGenerator:
    def __init__(self, api_key, model="gpt-4o"):
        """
        初始化生成器
        :param api_key: OpenAI API Key
        :param model: 推荐使用具有强逻辑和强创意理解能力的模型
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def _brainstorm_creative_concept(self, topic):
        """
        第一阶段：创意激荡（Brainstorming Node）
        通过高 temperature 和反向提示词，强行打破陈词滥调，生成独特的核心设定。
        """
        brainstorm_prompt = """
        你是一个顶级的皮克斯（Pixar）和宫崎骏风格的创意总监。
        你的任务是为给定的绘本主题构思一个极具创新性、反套路、充满视觉隐喻的核心概念。

        【硬性规则——打破陈词滥调】：
        1. 绝不使用“很久很久以前”、“在神秘的森林里”等俗套开篇。
        2. 必须引入【反差萌/不匹配设定（Juxtaposition）】：让主角拥有一种与其身份或任务完全相悖的特质（例如：极度怕水的海盗、恐高的小鸟、精通流体力学的企鹅）。
        3. 必须构思【视觉隐喻（Visual Metaphor）】：不要平铺直叙。比如表达“环境污染”，不要只画垃圾，可以画“天空是一块褪色、打着彩色补丁的旧桌布”。
        
        请输出如下 JSON 格式（不要包含任何 markdown 标记，纯 JSON）：
        {
            "core_twist": "核心剧情反转或新颖视角",
            "protagonist_name": "主角名字",
            "protagonist_concept": "主角独特的外貌特征与致命反差萌特质",
            "visual_style_tone": "独特的色彩与视觉风格隐喻"
        }
        """
        user_input = f"请为主题 '{topic}' 激发一个打破常规的、适合3-6岁儿童的绘本创意概念。"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": brainstorm_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.85, # 拔高创造力，允许模型“整活”
                response_format={ "type": "json_object" }
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"❌ 创意激荡阶段失败: {e}")
            return None

    def generate_full_package(self, topic):
        """
        第二阶段：结构化适配（Structuring Node）
        将天马行空的创意种子，在低 temperature 下严格束缚并格式化为标准的 Agent 任务书。
        """
        # 1. 先获取极具创新性的核心概念
        print("💡 正在激发创新灵感，打破陈词滥调...")
        concept = self._brainstorm_creative_concept(topic)
        if not concept:
            print("⚠️ 无法获取创意设定，降级为默认生成。")
            concept = {
                "core_twist": "传统故事线",
                "protagonist_name": "小机器人",
                "protagonist_concept": "一个蓝色的圆头机器人",
                "visual_style_tone": "明亮的卡通风格"
            }
        
        print(f"✨ 成功捕获核心创意：【{concept['protagonist_name']} -> {concept['core_twist'][:30]}...】")

        # 2. 将创意喂给结构化节点，严格卡死格式与低幻觉
        structuring_prompt = """
        你是一个严谨的 AI 智能体导演。
        你的任务是将给定的【创意概念种子】扩展并精准格式化为一个高度结构化的儿童互动绘本 JSON 任务书。
        
        必须无条件包含以下字段，并且每页的分镜必须紧扣给定的【创意反差】与【视觉隐喻】：
        1. story_id: 随机生成的唯一 ID。
        2. protagonist: 包含 name (名字) 和 visual_description (结合创意种子，给出极其详细的视觉特征，作为 Stable Diffusion 的锁死变量)。
        3. pages: 一个数组，每页包含：
           - scene_id: 页码。
           - narration: 给孩子读的旁白文本（文字要富有韵律感、幽默或诗意，避免大白话）。
           - visual_prompt: 专门给 Stable Diffusion 用的图像描述，必须包含主角特征、当前动作，以及融入给定的【视觉隐喻】。
           - motion_directive: 简单的动态指令（如：小猫在跳跃、星星在闪烁）。
           - interaction: 这一页结束后的互动问题（具有启发性）。
        4. rec_tags: 推荐系统用的标签（风格、情感、认知难度、主题）。
        """

        user_input = f"""
        基于以下创意概念，创作一个 3 页的互动绘本故事：
        ---
        【主题】: {topic}
        【核心反转】: {concept['core_twist']}
        【角色雏形】: {concept['protagonist_name']} ({concept['protagonist_concept']})
        【视觉与隐喻调性】: {concept['visual_style_tone']}
        ---
        请严格输出 JSON 格式。
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": structuring_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.2, # 降低变数，确保高度结构化、无幻觉、严格执行指令
                response_format={ "type": "json_object" }
            )
            
            story_data = json.loads(response.choices[0].message.content)
            story_data['meta_info'] = {
                "topic": topic,
                "version": "2.0_CreativeBoost",
                "generated_by": "DreamWeaver_SyntheticGenerator"
            }
            return story_data
        except Exception as e:
            print(f"❌ 结构化包装阶段失败: {e}")
            return None

    def save_to_file(self, data, filename=None):
        if not data:
            return
        if not filename:
            filename = f"story_{data.get('story_id', uuid.uuid4())}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"\n✅ 故事数据包已成功保存至: {filename}")

# --- 运行测试 ---
if __name__ == "__main__":
    # 从环境变量获取 API KEY
    MY_API_KEY = os.getenv("OPENAI_API_KEY") or "你的_OPENAI_API_KEY"
    
    if MY_API_KEY == "你的_OPENAI_API_KEY":
        print("🛑 请先配置您的 OpenAI API Key 再运行！")
    else:
        generator = SyntheticGenerator(api_key=MY_API_KEY)
        
        print("🚀 正在为您运行升级版的 AI 绘本生成器（前松后紧创新架构）...")
        result = generator.generate_full_package("小机器人学习如何保护地球环境")
        
        if result:
            generator.save_to_file(result)
            
            # 优雅地打印生成结果，直观查看创新性改善
            print("\n================== 💡 创新性效果预览 ==================")
            print(f"🌟 设定主角: {result['protagonist']['name']}")
            print(f"📝 视觉特征锁死变量: {result['protagonist']['visual_description']}\n")
            
            for page in result['pages']:
                print(f"--- [第 {page['scene_id']} 页] ---")
                print(f"📖 旁白: {page['narration']}")
                print(f"🎨 SD 图像 Prompt: {page['visual_prompt']}")
                print(f"👆 互动交互: {page['interaction']}\n")