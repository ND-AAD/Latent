#!/usr/bin/env python3
"""
WCAG Color Contrast Checker
Validates color combinations for accessibility compliance
"""

import re
from typing import Tuple, Dict

class ContrastChecker:
    """Check color contrast ratios for WCAG compliance"""

    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB values"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    @staticmethod
    def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
        """Convert RGB to hex color"""
        return '#{:02x}{:02x}{:02x}'.format(*rgb)

    @staticmethod
    def get_relative_luminance(rgb: Tuple[int, int, int]) -> float:
        """Calculate relative luminance of a color"""

        def adjust_channel(channel: int) -> float:
            c = channel / 255
            if c <= 0.03928:
                return c / 12.92
            return ((c + 0.055) / 1.055) ** 2.4

        r, g, b = [adjust_channel(c) for c in rgb]
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    def get_contrast_ratio(self, color1: str, color2: str) -> float:
        """
        Calculate contrast ratio between two colors

        Args:
            color1: Hex color string
            color2: Hex color string

        Returns:
            Contrast ratio (1:1 to 21:1)
        """
        rgb1 = self.hex_to_rgb(color1)
        rgb2 = self.hex_to_rgb(color2)

        lum1 = self.get_relative_luminance(rgb1)
        lum2 = self.get_relative_luminance(rgb2)

        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)

        return (lighter + 0.05) / (darker + 0.05)

    def check_wcag_compliance(self, ratio: float, text_size: str = "normal") -> Dict[str, bool]:
        """
        Check if contrast ratio meets WCAG standards

        Args:
            ratio: Contrast ratio
            text_size: "normal" or "large"

        Returns:
            Dict with AA and AAA compliance status
        """
        if text_size == "large":
            # Large text: ≥18px or ≥14px bold
            aa_threshold = 3.0
            aaa_threshold = 4.5
        else:
            # Normal text: <18px
            aa_threshold = 4.5
            aaa_threshold = 7.0

        return {
            "AA": ratio >= aa_threshold,
            "AAA": ratio >= aaa_threshold,
            "ratio": round(ratio, 2)
        }

    def suggest_colors(self, base_color: str, target_ratio: float = 4.5,
                      for_background: bool = True) -> list:
        """
        Suggest colors that meet target contrast ratio

        Args:
            base_color: Hex color to match against
            target_ratio: Minimum contrast ratio
            for_background: If True, suggest background colors; else text colors

        Returns:
            List of suggested hex colors
        """
        suggestions = []
        base_rgb = self.hex_to_rgb(base_color)
        base_lum = self.get_relative_luminance(base_rgb)

        # Calculate target luminance values
        if for_background:
            # We're finding backgrounds for the given text color
            target_lum_dark = (base_lum + 0.05) / target_ratio - 0.05
            target_lum_light = target_ratio * (base_lum + 0.05) - 0.05
        else:
            # We're finding text colors for the given background
            target_lum_dark = (base_lum + 0.05) / target_ratio - 0.05
            target_lum_light = target_ratio * (base_lum + 0.05) - 0.05

        # Generate suggestions (simplified - in practice would be more sophisticated)
        if target_lum_dark >= 0:
            # Suggest a dark color
            gray_value = int(target_lum_dark * 255)
            suggestions.append(self.rgb_to_hex((gray_value, gray_value, gray_value)))

        if target_lum_light <= 1:
            # Suggest a light color
            gray_value = int(target_lum_light * 255)
            suggestions.append(self.rgb_to_hex((gray_value, gray_value, gray_value)))

        return suggestions

def main():
    """Interactive contrast checker"""
    checker = ContrastChecker()

    print("WCAG Color Contrast Checker")
    print("=" * 40)
    print("Enter colors as hex values (e.g., #333333 or #333)")
    print()

    while True:
        print("\\nChoose an option:")
        print("1. Check contrast between two colors")
        print("2. Find accessible colors for a base color")
        print("3. Check a color palette")
        print("4. Exit")

        choice = input("\\nEnter choice (1-4): ")

        if choice == "1":
            color1 = input("Enter first color (text): ")
            color2 = input("Enter second color (background): ")
            text_size = input("Text size (normal/large): ").lower()

            try:
                ratio = checker.get_contrast_ratio(color1, color2)
                compliance = checker.check_wcag_compliance(ratio, text_size)

                print(f"\\nContrast Ratio: {ratio:.2f}:1")
                print(f"WCAG AA: {'✅ PASS' if compliance['AA'] else '❌ FAIL'}")
                print(f"WCAG AAA: {'✅ PASS' if compliance['AAA'] else '❌ FAIL'}")

                if not compliance['AA']:
                    min_ratio = 4.5 if text_size == "normal" else 3.0
                    print(f"\\n⚠️  Contrast ratio should be at least {min_ratio}:1 for AA compliance")

            except Exception as e:
                print(f"Error: {e}")

        elif choice == "2":
            base_color = input("Enter base color: ")
            color_type = input("Find (t)ext or (b)ackground colors? ").lower()
            level = input("WCAG level (AA/AAA): ").upper()

            target_ratio = 7.0 if level == "AAA" else 4.5
            for_background = color_type == 'b'

            try:
                suggestions = checker.suggest_colors(base_color, target_ratio, for_background)
                print(f"\\nSuggested colors for {level} compliance:")
                for color in suggestions:
                    ratio = checker.get_contrast_ratio(base_color, color)
                    print(f"  {color} - Ratio: {ratio:.2f}:1")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "3":
            print("\\nEnter your color palette (one hex color per line, empty line to finish):")
            colors = []
            while True:
                color = input()
                if not color:
                    break
                colors.append(color)

            if len(colors) < 2:
                print("Need at least 2 colors for comparison")
                continue

            print("\\n" + "="*50)
            print("Contrast Matrix (Normal Text)")
            print("="*50)
            print("       ", end="")
            for c in colors:
                print(f"{c:^10}", end="")
            print()

            for i, color1 in enumerate(colors):
                print(f"{color1:^7}", end="")
                for j, color2 in enumerate(colors):
                    if i == j:
                        print(f"{'---':^10}", end="")
                    else:
                        ratio = checker.get_contrast_ratio(color1, color2)
                        compliance = checker.check_wcag_compliance(ratio)
                        symbol = "✅" if compliance['AA'] else "❌"
                        print(f"{symbol} {ratio:.1f}:1", end="  ")
                print()

        elif choice == "4":
            print("Goodbye!")
            break

if __name__ == "__main__":
    main()