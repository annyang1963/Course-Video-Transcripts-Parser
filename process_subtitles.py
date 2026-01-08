import re
import pandas as pd
from glob import glob


def process_text(input_text):
    text = [x.replace("'", "") for x in input_text]
    text = [x.replace("\n", "") for x in text]
    text = [x.replace('"', '') for x in text]
    text = [x.replace(',', '') for x in text]
    text = [x.lower() for x in text]
    return text


def get_details_from_srt_path(path_to_srt):
    nd = path_to_srt.split('/')[1:][0].split('_')[0]
    course = path_to_srt.split('/')[1:][0].split('_')[1]
    lesson = path_to_srt.split('/')[1:][0].split('_')[2]
    page = path_to_srt.split('/')[1:][1]
    return nd, course, lesson, page


def get_text_timestamp(path_to_srt):

    with open(path_to_srt, 'r') as h:
        sub = h.readlines()

    nd = path_to_srt.split('/')[1:][0].split('_')[0]
    course = path_to_srt.split('/')[1:][0].split('_')[1]
    lesson = path_to_srt.split('/')[1:][0].split('_')[2]
    page = path_to_srt.split('/')[1:][1]

    re_pattern = r'[0-9]{2}:[0-9]{2}:[0-9]{2},[0-9]{3} -->'
    regex = re.compile(re_pattern)
    # Get start times
    start_times = list(filter(regex.search, sub))
    start_times = [time.split(' ')[0] for time in start_times]
    # Get lines
    lines = [[]]
    for sentence in sub:
        if re.match(re_pattern, sentence):
            lines[-1].pop()
            lines.append([])
        else:
            lines[-1].append(sentence)
    lines = lines[1:]         

    # Merge results
    subs = {start_time:line for start_time,line in zip(start_times, lines)}

    for key, value in subs.items():
            value = value[0]
            subs[key] = value

    timestamp = list(subs.keys())
    # process text_to_update
    text = process_text(subs.values())

    result_df = pd.DataFrame({'Timestamp': timestamp, 'Text': text})
    result_df['ND'] = nd
    result_df['Course'] = course
    result_df['Lesson'] = lesson
    result_df['Page'] = page
    return result_df


def main():

    with open('keywords.txt') as f:
        keyword_list = process_text(f.readlines())

    all_course_transcripts = glob('transcripts/*/*_en*')
    updated_df = pd.DataFrame({'ND': [], 'Course': [], 'Lesson': [], 'Page': [], 'Timestamp': [], 'Text': []})
    print(keyword_list)

    for path_to_srt in all_course_transcripts:
        # print(path_to_srt)
        full_transcript_df = get_text_timestamp(path_to_srt)
        # nd, course, lesson, page = get_details_from_srt_path(path_to_srt)

        for keyword in keyword_list:
            nd_mention = full_transcript_df.loc[full_transcript_df['Text'].str.contains(keyword, case=False)]
            updated_df = updated_df.append(nd_mention, ignore_index=True)

    updated_df.drop_duplicates(keep='first', inplace=True, ignore_index=True)

    updated_df.to_csv('results.csv')


if __name__ == '__main__':
    main()