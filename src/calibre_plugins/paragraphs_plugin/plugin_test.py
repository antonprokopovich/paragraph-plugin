import logging

logging.basicConfig(
    format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG
)


def split_paragraphs2(content):
    lines = content.split('.')
    logging.info(f"[Split paragraphs plugin] lines: {lines}\n\n")

    new_content = []
    paragraph = []

    logging.info(f"[Split paragraphs plugin] will parse {len(lines)} lines")

    for line in lines:
        paragraph.append(line + ".")
        if len(paragraph) == 4:
            new_content.append(' '.join(paragraph) + '\n')
            paragraph = []

    if paragraph:
        new_content.append(' '.join(paragraph))

    # new_content = '\n'.join(new_content)

    return new_content


if __name__ == "__main__":
    # path_to_book = "/Users/anton/sample3.txt"
    #
    # SplitParagraphsPlugin.split_book(path_to_book)


    ## Test on string.

    sample_content = """
    The sun dipped below the horizon, painting the sky with hues of orange and purple. A gentle breeze rustled through the trees, carrying with it the scent of pine. In the distance, the sound of waves crashing against the shore echoed softly. Birds chirped their final melodies of the day as the world slowly transitioned into night. Maria sat on the porch, sipping her tea, lost in thought. She had always found peace in these quiet moments, away from the chaos of her daily routine. The city, though vibrant, often overwhelmed her with its noise and pace. Here, in the countryside, time seemed to slow down, giving her space to breathe.

    As the stars began to twinkle in the clear night sky, Maria wondered what the future held for her. She had dreams, big ones, but the path to them often felt uncertain. Her phone buzzed beside her, snapping her out of her reverie. A message from an old friend lit up the screen, reminding her of the connections she cherished but sometimes neglected. Smiling, she typed a quick reply, promising to catch up soon. The sound of crickets filled the air, adding to the symphony of the night. She pulled her shawl tighter around her shoulders as the temperature dropped. The night was still young, but Maria felt a sense of calm wash over her. Tomorrow, she would face the world again, but for now, she allowed herself to simply be.
    """
    new_content = split_paragraphs2(sample_content)

    print("\nnew content: ", new_content)
