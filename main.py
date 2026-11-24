from manim import *


class StackSecurityCookies(Scene):
    def construct(self):

        self.camera.background_color = "#0D1117"

        # =========================================================
        # GIÁ TRỊ MINH HỌA
        # =========================================================

        rsp_before = 0x000000A1F0FFF8C0
        rsp_after  = rsp_before - 0x38          # RSP sau lệnh `sub rsp, 38h`

        # Giá trị mặc định (build-time constant)
        default_cookie = 0x00002B992DDFA232

        # Giá trị "đã XOR" thực tế (runtime) — khác default để tránh gây hiểu nhầm
        global_cookie = 0x00007FF6A1B2C3D4

        # Sau: xor rax, rsp
        encoded_cookie = global_cookie ^ rsp_after

        # [rsp + 38h + var_10] với var_10 = -10h  =>  [rsp + 28h]
        cookie_address = rsp_after + 0x28

        # [rsp + 38h + var_18] với var_18 = -18h  =>  [rsp + 20h]
        a_address = rsp_after + 0x20


        # =========================================================
        # 1. TITLE
        # =========================================================

        title_text = Text(
            "Stack Security Cookies",
            font_size=40,
            weight=BOLD,
            color=WHITE,
        ).move_to(ORIGIN)

        self.play(Write(title_text))
        self.wait(1)
        self.play(FadeOut(title_text))


        # =========================================================
        # 2. SOURCE C++ (SỬA LỖI DẤU CHẤM VÀ CĂN LỀ SỐ DÒNG)
        # =========================================================

        cpp_code = """<span foreground="#FF7B72">#include</span> <span foreground="#A5D6FF">&lt;iostream&gt;</span>
<span foreground="#FF7B72">using namespace</span> std;

<span foreground="#FF7B72">int</span> <span foreground="#D2A8FF">main</span>()
{
    <span foreground="#FF7B72">int</span> a;
    cin &gt;&gt; a;

    cout &lt;&lt; a + <span foreground="#A5D6FF">10</span>;

    <span foreground="#FF7B72">return</span> <span foreground="#A5D6FF">0</span>;
}"""

        # Tạo text cho code (Thêm line_spacing để khớp với số dòng)
        Source_code = MarkupText(
            cpp_code,
            font="Consolas",
            font_size=20,
            color="#C9D1D9",
            line_spacing=1.2,
        )

        # Tạo số dòng (Dùng cùng font_size và line_spacing với code)
        num_lines = len(cpp_code.split('\n'))
        line_numbers = VGroup()
        for i in range(1, num_lines + 1):
            num = Text(str(i), font="Consolas", font_size=20, color="#858585")
            line_numbers.add(num)
        
        # Căn chỉnh số dòng thẳng hàng dọc
        line_numbers.arrange(DOWN, buff=0.12, aligned_edge=RIGHT)
        
        # Đảm bảo cột số dòng có cùng chiều cao với Source_code
        line_numbers.align_to(Source_code, UP)
        line_numbers.set_height(Source_code.height)

        # Gom số dòng và code lại (căn đỉnh - UP)
        inner_content = VGroup(line_numbers, Source_code)
        inner_content.arrange(RIGHT, buff=0.3, aligned_edge=UP)

        # Khung VS Code
        padding = 0.3
        editor_bg = RoundedRectangle(
            width=inner_content.width + padding * 2,
            height=inner_content.height + padding * 2,
            corner_radius=0.12, fill_color="#1E1E1E", fill_opacity=1,
            stroke_color="#3C3C3C", stroke_width=2,
        ).move_to(inner_content.get_center())

        # Thanh tiêu đề
        title_bar = RoundedRectangle(
            width=editor_bg.width, height=0.3, corner_radius=0.12,
            fill_color="#2D2D2D", fill_opacity=1, stroke_width=0,
        ).align_to(editor_bg, UP)

        title_bar_cover = Rectangle(
            width=title_bar.width, height=0.15,
            fill_color="#2D2D2D", fill_opacity=1, stroke_width=0,
        ).align_to(title_bar, DOWN)

        # 3 dấu chấm (Đã sửa vị trí dịch sang phải, nằm bên trong thanh tiêu đề)
        dots = VGroup(*[
            Dot(radius=0.05, color=c, fill_opacity=1)
            for c in ["#FF5F56", "#FFBD2E", "#27C93F"]
        ]).arrange(RIGHT, buff=0.1)
        # Đặt các dấu chấm ở góc trái của thanh tiêu đề, cách mép trái một khoảng
        dots.next_to(title_bar.get_corner(UL), RIGHT, buff=0.2)
        dots.align_to(title_bar, UP).shift(DOWN * 0.15)

        # Tên file
        filename = Text("main.cpp", font="Consolas", font_size=12, color="#CCCCCC").move_to(title_bar.get_center())

        # Gom tất cả thành editor
        editor = VGroup(editor_bg, title_bar, title_bar_cover, dots, filename, inner_content)
        editor.to_edge(LEFT, buff=0.8).shift(UP * 0.2)

        self.play(FadeIn(editor, shift=RIGHT * 0.3), run_time=1.2)
        self.wait(1.5)

        # =========================================================
        # 3. COMPILE ARROW
        # =========================================================

        arrow = Arrow(LEFT, RIGHT, color=YELLOW)
        arrow.move_to(editor.get_right() + RIGHT * 1.5)
        self.play(GrowArrow(arrow))


        # =========================================================
        # 4. ASSEMBLY (SỬA: 1 khung bao ngoài, không kẻ từng dòng)
        # =========================================================

        asm_lines = [
            '<span foreground="#8B949E">; __unwind { // __GSHandlerCheck</span>',
            '<span foreground="#FF7B72">sub</span>     <span foreground="#79C0FF">rsp</span>, <span foreground="#A5D6FF">38h</span>',
            '<span foreground="#FF7B72">mov</span>     <span foreground="#79C0FF">rax</span>, cs:__security_cookie',
            '<span foreground="#FF7B72">xor</span>     <span foreground="#79C0FF">rax</span>, <span foreground="#79C0FF">rsp</span>',
            '<span foreground="#FF7B72">mov</span>     [<span foreground="#79C0FF">rsp</span>+<span foreground="#A5D6FF">38h</span>+var_10], <span foreground="#79C0FF">rax</span>',
            '<span foreground="#FF7B72">mov</span>     <span foreground="#79C0FF">rcx</span>, cs:std_cin',
            '<span foreground="#FF7B72">lea</span>     <span foreground="#79C0FF">rdx</span>, [<span foreground="#79C0FF">rsp</span>+<span foreground="#A5D6FF">38h</span>+a]',
            '<span foreground="#FF7B72">call</span>    cs:istream_read_int',
            '<span foreground="#FF7B72">mov</span>     <span foreground="#79C0FF">edx</span>, [<span foreground="#79C0FF">rsp</span>+<span foreground="#A5D6FF">38h</span>+a]',
            '<span foreground="#FF7B72">mov</span>     <span foreground="#79C0FF">rcx</span>, cs:std__cout',
            '<span foreground="#FF7B72">add</span>     <span foreground="#79C0FF">edx</span>, <span foreground="#A5D6FF">0Ah</span>',
            '<span foreground="#FF7B72">call</span>    cs:ostream_write_int',
            '<span foreground="#FF7B72">xor</span>     <span foreground="#79C0FF">eax</span>, <span foreground="#79C0FF">eax</span>',
            '<span foreground="#FF7B72">mov</span>     <span foreground="#79C0FF">rcx</span>, [<span foreground="#79C0FF">rsp</span>+<span foreground="#A5D6FF">38h</span>+var_10]',
            '<span foreground="#FF7B72">xor</span>     <span foreground="#79C0FF">rcx</span>, <span foreground="#79C0FF">rsp</span>        <span foreground="#8B949E">; StackCookie</span>',
            '<span foreground="#FF7B72">call</span>    __security_check_cookie',
            '<span foreground="#FF7B72">add</span>     <span foreground="#79C0FF">rsp</span>, <span foreground="#A5D6FF">38h</span>',
            '<span foreground="#FF7B72">retn</span>',
            '<span foreground="#8B949E">; }</span>',
        ]

        # Tạo text cho từng dòng, KHÔNG có box riêng
        asm_texts = VGroup()
        for line in asm_lines:
            asm_text = MarkupText(
                line,
                font="Consolas",
                font_size=12,
                color="#C9D1D9",
            )
            asm_texts.add(asm_text)

        asm_texts.arrange(DOWN, aligned_edge=LEFT, buff=0.08)

        # 1 khung duy nhất bao quanh toàn bộ khối assembly
        asm_frame = SurroundingRectangle(
            asm_texts,
            color="#8B949E",
            buff=0.18,
            stroke_width=2,
        )

        # Gom frame + texts thành 1 group để di chuyển
        assembly_group = VGroup(asm_frame, asm_texts)
        assembly_group.to_edge(RIGHT, buff=0.5)

        self.play(FadeIn(assembly_group), run_time=1)
        self.wait(1)


        # =========================================================
        # 5. XÓA C++ + COMPILE ARROW
        # =========================================================

        self.play(FadeOut(editor), FadeOut(arrow))


        # =========================================================
        # 6. ASSEMBLY CHUYỂN SANG TRÁI
        # =========================================================

        self.play(
            assembly_group.animate.to_edge(LEFT, buff=0.6),
            run_time=1,
        )


        # =========================================================
        # 7. HIGHLIGHT SECURITY COOKIE (encode / decode)
        # =========================================================

        create_highlight = SurroundingRectangle(
            VGroup(
                asm_texts[2],
                asm_texts[3],
                asm_texts[4],
            ),
            color=YELLOW,
            buff=0.08,
            stroke_width=3,
        )

        check_highlight = SurroundingRectangle(
            VGroup(
                asm_texts[13],
                asm_texts[14],
                asm_texts[15],
            ),
            color=RED,
            buff=0.08,
            stroke_width=3,
        )

        self.play(Create(create_highlight), Create(check_highlight))
        self.wait(2)
        self.play(FadeOut(create_highlight), FadeOut(check_highlight))


        # =========================================================
        # 8. POINTER CHỈ INSTRUCTION + NHÃN RIP (CHỈ HIỆN 1 LẦN)
        # =========================================================

        pointer = Arrow(
            LEFT, RIGHT,
            color=YELLOW,
            stroke_width=4,
            max_tip_length_to_length_ratio=0.1,
        )
        pointer.scale(0.4)
        pointer.next_to(asm_texts[0], LEFT, buff=0.2)

        rip_label = Text(
            "RIP",
            font="Consolas",
            font_size=14,
            weight=BOLD,
            color=RED,
        ).next_to(pointer, UP, buff=0.05) # Nhãn nằm trên mũi tên

        self.play(GrowArrow(pointer), FadeIn(rip_label))
        
        # Lưu lại tọa độ ban đầu của mũi tên (để chút nữa làm mờ chữ RIP)
        original_pointer_pos = pointer.get_center()


        # =========================================================
        # 9. CPU REGISTERS
        # =========================================================

        register_title = Text(
            "CPU REGISTERS",
            font="Consolas",
            font_size=18,
            weight=BOLD,
            color="#58D3F7",
        ).move_to(RIGHT * 5 + UP * 3)

        register_box = Rectangle(
            width=4,
            height=1.35,
            stroke_color="#58D3F7",
            stroke_width=2,
        ).next_to(register_title, DOWN, buff=0.1)

        rax_label = Text("RAX:", font="Consolas", font_size=14, color=WHITE)
        rax_value = Text("????????????????", font="Consolas",
                         font_size=14, color="#79C0FF")
        rax_row   = VGroup(rax_label, rax_value).arrange(RIGHT, buff=0.2)

        rcx_label = Text("RCX:", font="Consolas", font_size=14, color=WHITE)
        rcx_value = Text("????????????????", font="Consolas",
                         font_size=14, color="#D2A8FF")
        rcx_row   = VGroup(rcx_label, rcx_value).arrange(RIGHT, buff=0.2)

        rsp_label = Text("RSP:", font="Consolas", font_size=14, color=WHITE)
        rsp_value = Text(f"0x{rsp_before:016X}", font="Consolas",
                         font_size=14, color="#7EE787")
        rsp_row   = VGroup(rsp_label, rsp_value).arrange(RIGHT, buff=0.2)

        register_rows = VGroup(rax_row, rcx_row, rsp_row)
        register_rows.arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        register_rows.move_to(register_box.get_center())

        self.play(
            FadeIn(register_title),
            Create(register_box),
            FadeIn(register_rows),
        )


        # =========================================================
        # 10. GLOBAL MEMORY
        # =========================================================

        global_title = Text(
            "GLOBAL MEMORY",
            font="Consolas",
            font_size=16,
            weight=BOLD,
            color="#FFA657",
        ).next_to(register_box, DOWN, buff=0.5)

        global_box = Rectangle(
            width=4,
            height=1.05,
            stroke_color="#FFA657",
            stroke_width=2,
        ).next_to(global_title, DOWN, buff=0.08)

        section_label = Text(
            "Section: .data",
            font="Consolas",
            font_size=11,
            color="#8B949E",
        )

        global_cookie_label = Text(
            "__security_cookie",
            font="Consolas",
            font_size=13,
            color=WHITE,
        )

        global_cookie_value = Text(
            f"0x{global_cookie:016X}",
            font="Consolas",
            font_size=14,
            color="#FFA657",
        )

        global_content = VGroup(
            section_label,
            global_cookie_label,
            global_cookie_value,
        )
        global_content.arrange(DOWN, buff=0.05)
        global_content.move_to(global_box.get_center())

        self.play(
            FadeIn(global_title),
            Create(global_box),
            FadeIn(global_content),
        )


        # =========================================================
        # 11. STACK FRAME
        # =========================================================
        # Hướng sơ đồ: ĐỊA CHỈ CAO Ở TRÊN, ĐỊA CHỈ THẤP Ở DƯỚI
        # Offset tính từ RSP hiện tại (rsp_after):
        #   [RSP+38h] -> return address
        #   [RSP+28h] -> __security_cookie
        #   [RSP+20h] -> a
        #   [RSP+00h] -> RSP hiện tại
        # =========================================================

        stack_title = Text(
            "STACK FRAME",
            font="Consolas",
            font_size=16,
            weight=BOLD,
            color="#7EE787",
        ).next_to(global_box, DOWN, buff=0.5)

        stack_labels = [
            "[RSP+38h] Return Addr",
            "[RSP+28h] Cookie",
            "[RSP+20h] a",
            "[RSP+00h] RSP",
        ]

        stack_group = VGroup()

        for label in stack_labels:
            stack_box = Rectangle(
                width=4,
                height=0.38,
                stroke_color="#8B949E",
                stroke_width=1,
            )
            stack_text = Text(
                label,
                font="Consolas",
                font_size=10,
                color="#C9D1D9",
            )
            stack_text.move_to(
                stack_box.get_left() + RIGHT * 0.12,
                aligned_edge=LEFT,
            )
            stack_group.add(VGroup(stack_box, stack_text))

        stack_group.arrange(DOWN, buff=0)
        stack_group.next_to(stack_title, DOWN, buff=0.08)

        self.play(FadeIn(stack_title), FadeIn(stack_group))
        self.wait(1)


        # =========================================================
        # 12. sub rsp, 38h
        # =========================================================

        # self.play(
        #     rip_pointer.animate.next_to(
        #         asm_texts[1], LEFT, buff=0.25,
        #     )
        # )

        # Làm mờ chữ RIP và di chuyển mũi tên đến dòng số 1 (index 1)
        self.play(
            FadeOut(rip_label), # Xóa chữ RIP
            pointer.animate.next_to(asm_texts[1], LEFT, buff=0.2),
            run_time=0.5
        )

        # explanation = Text(
        #     "RSP = RSP - 0x38",
        #     font="Consolas",
        #     font_size=16,
        #     color=YELLOW,
        # )
        # self.play(FadeIn(explanation))

        # calculate = Text(
        #     f"= 0x{rsp_before:016X} - 0x38",
        #     font="Consolas",
        #     font_size=16,
        #     color=YELLOW,
        # ).next_to(explanation, DOWN, buff=0.1)
        # self.play(FadeIn(calculate))

        # result = Text(
        #     f"= 0x{rsp_after:016X}",
        #     font="Consolas",
        #     font_size=16,
        #     color=YELLOW,
        # ).next_to(calculate, DOWN, buff=0.1)
        # self.play(FadeIn(result))

        new_rsp_value = Text(
            f"0x{rsp_after:016X}",
            font="Consolas",
            font_size=14,
            color="#7EE787",
        ).move_to(rsp_value.get_center())

        self.play(ReplacementTransform(rsp_value, new_rsp_value))
        rsp_value = new_rsp_value

        #self.wait(1.5)

        # self.play(
        #     FadeOut(explanation),
        #     FadeOut(calculate),
        #     FadeOut(result),
        # )


        # =========================================================
        # 12.5 NGUỒN GỐC __security_cookie (ĐÃ THU NHỎ VỪA VẶN)
        # =========================================================

        # 1. Tiêu đề (Giảm font size)
        where_title = Text(
            "__security_init_cookie() is NOT in main",
            font="Consolas", font_size=16, weight=BOLD, color=RED
        )

        # 2. Giải thích (Giảm font size)
        where_explain = Text(
            "It is called automatically by the CRT (C Runtime)\n"
            "at the Entry Point (before main starts).",
            font="Consolas", font_size=12, color="#C9D1D9"
        ).next_to(where_title, DOWN, buff=0.15)

        # 3. Đoạn mã minh họa Entry Point (Giảm font size)
        entry_code = """
        <span foreground="#8B949E">; Entry Point (mainCRTStartup)</span>
        <span foreground="#FF7B72">sub</span>     <span foreground="#79C0FF">rsp</span>, <span foreground="#A5D6FF">28h</span>
        <span foreground="#FF7B72">call</span>    <span foreground="#DCDCAA">__security_init_cookie</span>  <span foreground="#8B949E">; Initialize here</span>
        <span foreground="#FF7B72">add</span>     <span foreground="#79C0FF">rsp</span>, <span foreground="#A5D6FF">28h</span>
        <span foreground="#FF7B72">call</span>    <span foreground="#DCDCAA">__scrt_common_main_seh</span> <span foreground="#8B949E">; Call main()</span>
        """
        entry_code_obj = MarkupText(
            entry_code, font="Consolas", font_size=12, color="#C9D1D9"
        ).next_to(where_explain, DOWN, buff=0.25)

        # # Khung bao quanh
        # entry_frame = SurroundingRectangle(
        #     entry_code_obj, color=YELLOW, buff=0.15, stroke_width=2
        # )

        # Gom tất cả thành 1 nhóm, đặt ở chính giữa và đẩy lên trên 1 chút
        init_group = VGroup(where_title, where_explain, entry_code_obj) #, entry_frame)
        init_group.move_to(ORIGIN).shift(UP * 0.3)

        self.play(FadeIn(init_group, shift=DOWN * 0.2), run_time=1)
        self.wait(2)
        
        # Dọn dẹp
        self.play(FadeOut(init_group), run_time=0.5)
        # =========================================================
        # 13. mov rax, cs:__security_cookie
        # =========================================================

        self.play(
            pointer.animate.next_to(
                asm_texts[2], LEFT, buff=0.25,
            )
        )

        explanation = Text(
            "RAX = __security_cookie",
            font="Consolas",
            font_size=16,
            color="#79C0FF",
        )
        self.play(FadeIn(explanation))

        result = Text(
            f"= 0x{global_cookie:016X}",
            font="Consolas",
            font_size=16,
            color="#79C0FF",
        ).next_to(explanation, DOWN, buff=0.1)
        self.play(FadeIn(result))

        moving_cookie = global_cookie_value.copy()
        self.add(moving_cookie)

        self.play(
            moving_cookie.animate.move_to(rax_value.get_center()),
            FadeOut(rax_value),
            run_time=1,
        )
        self.remove(moving_cookie)

        new_rax_value = Text(
            f"0x{global_cookie:016X}",
            font="Consolas",
            font_size=14,
            color="#79C0FF",
        ).move_to(rax_value.get_center())

        self.add(new_rax_value)
        rax_value = new_rax_value

        self.wait(1)
        self.play(FadeOut(explanation), FadeOut(result))


        # =========================================================
        # 14. xor rax, rsp
        # =========================================================

        self.play(
            pointer.animate.next_to(
                asm_texts[3], LEFT, buff=0.25,
            )
        )

        xor_formula = VGroup(
            Text("RAX = RAX XOR RSP", font="Consolas",
                 font_size=14, color=YELLOW),
            Text(
                f"= 0x{global_cookie:016X} XOR 0x{rsp_after:016X}",
                font="Consolas", font_size=14, color=YELLOW,
            ),
            Text(
                f"= 0x{encoded_cookie:016X}",
                font="Consolas", font_size=14, color=YELLOW,
            ),
        ).arrange(DOWN, buff=0.08).move_to(ORIGIN)

        self.play(FadeIn(xor_formula))
        self.wait(1)

        encoded_rax_value = Text(
            f"0x{encoded_cookie:016X}",
            font="Consolas",
            font_size=14,
            color=YELLOW,
        ).move_to(rax_value.get_center())

        self.play(ReplacementTransform(rax_value, encoded_rax_value))
        rax_value = encoded_rax_value

        self.wait(1.5)
        self.play(FadeOut(xor_formula))


        # =========================================================
        # 15. mov [rsp+38h+var_10], rax
        # =========================================================

        self.play(
            pointer.animate.next_to(
                asm_texts[4], LEFT, buff=0.25,
            )
        )

        address_formula = VGroup(
            Text("[RSP + 38h + var_10]", font="Consolas",
                 font_size=14, color=WHITE),
            # Text("var_10 = -10h", font="Consolas",
            #      font_size=14, color=WHITE),
            Text("[RSP + 38h - 10h]", font="Consolas",
                 font_size=14, color=YELLOW),
            Text("= [RSP + 28h]", font="Consolas",
                 font_size=14, color=GREEN),
        ).arrange(DOWN, buff=0.07)

        self.play(FadeIn(address_formula))
        self.wait(1)
        self.play(FadeOut(address_formula))


        # =========================================================
        # 16. RAX -> STACK [RSP+28h]
        # =========================================================

        cookie_to_stack = rax_value.copy()
        self.add(cookie_to_stack)

        security_cookie_value = Text(
            f"{encoded_cookie:016X}",
            font="Consolas",
            font_size=10,
            color=YELLOW,
        )

        stack_cookie_content = VGroup(security_cookie_value)
        stack_cookie_content.arrange(RIGHT, buff=0.08)
        stack_cookie_content.move_to(stack_group[1][0].get_center())
        stack_cookie_content.shift(RIGHT * 0.65)

        self.play(
            cookie_to_stack.animate.scale(0.65).move_to(
                stack_cookie_content.get_center()
            ),
            run_time=1,
        )

        self.remove(cookie_to_stack)
        self.add(stack_cookie_content)


        # =========================================================
        # 17. Tua nhanh instr 5-6
        # =========================================================

        for i in [5, 6]:
            self.play(
                pointer.animate.next_to(
                    asm_texts[i], LEFT, buff=0.2,
                ),
                run_time=0.25,
            )


        # =========================================================
        # 18. call cs:istream_read_int
        # =========================================================

        self.play(
            pointer.animate.next_to(
                asm_texts[7], LEFT, buff=0.25,
            ),
            run_time=0.4,
        )

        input_text = Text(
            "User input: a",
            font="Consolas",
            font_size=15,
            color=YELLOW,
        )
        self.play(FadeIn(input_text))
        self.wait(0.7)


        # =========================================================
        # a có giá trị trên stack tại [RSP + 20h] (var_18)
        # =========================================================

        a_stack_value = Text(
            "a",
            font="Consolas",
            font_size=11,
            color="#58D3F7",
        )

        a_stack_value.move_to(stack_group[2][0].get_center())
        a_stack_value.shift(RIGHT * 0.8)

        a_to_stack = Text(
            "a",
            font="Consolas",
            font_size=15,
            color=YELLOW,
        ).move_to(input_text.get_center())

        self.add(a_to_stack)

        self.play(
            a_to_stack.animate.scale(0.7).move_to(
                a_stack_value.get_center()
            ),
            run_time=1,
        )

        self.remove(a_to_stack)
        self.add(a_stack_value)
        self.play(FadeOut(input_text))


        # =========================================================
        # 19. CÁC LỆNH CÒN LẠI CHẠY NHANH (8-12)
        # =========================================================

        for i in range(8, 13):
            self.play(
                pointer.animate.next_to(
                    asm_texts[i], LEFT, buff=0.2,
                ),
                run_time=0.2,
            )


        # =========================================================
        # 20. mov rcx, [rsp+38h+var_10]
        # =========================================================

        self.play(
            pointer.animate.next_to(
                asm_texts[13], LEFT, buff=0.25,
            ),
            run_time=0.4,
        )

        load_text = Text(
            "RCX <- [RSP + 28h]",
            font="Consolas",
            font_size=16,
            color="#D2A8FF",
        )
        self.play(FadeIn(load_text))

        stack_cookie_copy = security_cookie_value.copy()
        self.add(stack_cookie_copy)

        self.play(
            stack_cookie_copy.animate.scale(1.4).move_to(
                rcx_value.get_center()
            ),
            FadeOut(rcx_value),
            run_time=1,
        )
        self.remove(stack_cookie_copy)

        new_rcx_value = Text(
            f"0x{encoded_cookie:016X}",
            font="Consolas",
            font_size=14,
            color="#D2A8FF",
        ).move_to(rcx_value.get_center())

        self.add(new_rcx_value)
        rcx_value = new_rcx_value

        self.wait(1)
        self.play(FadeOut(load_text))


        # =========================================================
        # 21. xor rcx, rsp
        # =========================================================

        self.play(
            pointer.animate.next_to(
                asm_texts[14], LEFT, buff=0.25,
            )
        )

        decode_formula = VGroup(
            Text(f"RCX = 0x{encoded_cookie:016X}", font="Consolas",
                 font_size=13, color="#D2A8FF"),
            Text(f"RSP = 0x{rsp_after:016X}", font="Consolas",
                 font_size=13, color="#7EE787"),
            Text("RCX = RCX XOR RSP", font="Consolas",
                 font_size=14, color=YELLOW),
            Text(f"= {encoded_cookie:016X} XOR {rsp_after:016X}",
                 font="Consolas", font_size=14, color=YELLOW),
            Text(f"= 0x{global_cookie:016X}", font="Consolas",
                 font_size=14, color=YELLOW),
        ).arrange(DOWN, buff=0.08)

        self.play(FadeIn(decode_formula))
        self.wait(1)

        decoded_rcx_value = Text(
            f"0x{global_cookie:016X}",
            font="Consolas",
            font_size=14,
            color=GREEN,
        ).move_to(rcx_value.get_center())

        self.play(ReplacementTransform(rcx_value, decoded_rcx_value))
        rcx_value = decoded_rcx_value

        self.wait(2)
        self.play(FadeOut(decode_formula))


        # =========================================================
        # 22. call __security_check_cookie
        # =========================================================

        self.play(
            pointer.animate.next_to(
                asm_texts[15], LEFT, buff=0.25,
            )
        )

        check_title = Text(
            "__security_check_cookie()",
            font="Consolas",
            font_size=18,
            color=RED,
        )
        self.play(FadeIn(check_title))

        recovered_text = Text(
            f"RCX    : 0x{global_cookie:016X}",
            font="Consolas", font_size=13, color=GREEN,
        )
        expected_text = Text(
            f"GLOBAL : 0x{global_cookie:016X}",
            font="Consolas", font_size=13, color="#FFA657",
        )

        comparison = VGroup(recovered_text, expected_text)
        comparison.arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        comparison.next_to(check_title, DOWN, buff=0.2)

        self.play(FadeIn(comparison))
        self.wait(1)

        equal_text = Text(
            "==",
            font="Consolas",
            font_size=28,
            weight=BOLD,
            color=GREEN,
        ).next_to(comparison, DOWN, buff=0.15)

        valid_text = Text(
            "COOKIE VALID",
            font="Consolas",
            font_size=20,
            weight=BOLD,
            color=GREEN,
        ).next_to(equal_text, DOWN, buff=0.1)

        self.play(FadeIn(equal_text), FadeIn(valid_text))
        self.wait(2)

        self.play(
            FadeOut(check_title),
            FadeOut(comparison),
            FadeOut(equal_text),
            FadeOut(valid_text),
        )


        # =========================================================
        # 23. add rsp, 38h
        # =========================================================

        self.play(
            pointer.animate.next_to(
                asm_texts[16], LEFT, buff=0.25,
            )
        )

        restore_text = Text(
            "RSP = RSP + 0x38",
            font="Consolas",
            font_size=16,
            color=YELLOW,
        )
        self.play(FadeIn(restore_text))

        restored_rsp_value = Text(
            f"0x{rsp_before:016X}",
            font="Consolas",
            font_size=14,
            color="#7EE787",
        ).move_to(rsp_value.get_center())

        self.play(ReplacementTransform(rsp_value, restored_rsp_value))
        rsp_value = restored_rsp_value

        self.wait(1.5)
        self.play(FadeOut(restore_text))


        # =========================================================
        # 24. retn
        # =========================================================

        self.play(
            pointer.animate.next_to(
                asm_texts[17], LEFT, buff=0.25,
            )
        )

        return_text = Text(
            "SAFE RETURN",
            font="Consolas",
            font_size=26,
            weight=BOLD,
            color=GREEN,
        )

        self.play(FadeIn(return_text))
        self.wait(3)