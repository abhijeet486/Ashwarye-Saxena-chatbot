import fitz  # PyMuPDF
import torch
# Open the PDF file
pdf_document = 'QBcnw.pdf'
doc = fitz.open(pdf_document)
device = "cuda" if torch.cuda.is_available() else "mps" if torch.has_mps or torch.backends.mps.is_available() else "cpu"
print("Using device:", device)
if (device == 'cuda'):
    print(f"Device name: {torch.cuda.get_device_name(device.index)}")
    print(f"Device memory: {torch.cuda.get_device_properties(device.index).total_memory / 1024 ** 3} GB")
elif (device == 'mps'):
    print(f"Device name: <mps>")
else:
    print("NOTE: If you have a GPU, consider using it for training.")
    print("      On a Windows machine with NVidia GPU, check this video: https://www.youtube.com/watch?v=GMSjDTU8Zlc")
    print("      On a Mac machine, run: pip3 install --pre torch torchvision torchaudio torchtext --index-url https://download.pytorch.org/whl/nightly/cpu")
device = torch.device(device)
# Function to extract questions and options
def extract_questions_and_options(page_text):
    import re
    questions_and_options = []
    # Regex pattern to match questions and options
    pattern = re.compile(r'\d+\.\s+(.*?)\s+\(a\)\s+(.*?)\s+\(b\)\s+(.*?)\s+\(c\)\s+(.*?)\s+\(d\)\s+(.*?)(?=\d+\.\s+|$)', re.DOTALL)
    matches = pattern.findall(page_text)
    for match in matches:
        question = match[0].strip()
        options = [match[1].strip(), match[2].strip(), match[3].strip(), match[4].strip()]
        questions_and_options.append((question, options))
    return questions_and_options

# Iterate through each page and extract questions and options
all_questions_and_options = []
for page_num in range(len(doc)):
    page = doc.load_page(page_num)
    page_text = page.get_text()
    questions_and_options = extract_questions_and_options(page_text)
    all_questions_and_options.extend(questions_and_options)



from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

# Load the model and tokenizer
model_name = 'facebook/m2m100_418M'
tokenizer = M2M100Tokenizer.from_pretrained(model_name)
model = M2M100ForConditionalGeneration.from_pretrained(model_name)

# Function to translate English text to Hindi
def translate(text, src_lang='en', tgt_lang='hi'):
    # Set the source and target language tokens
    tokenizer.src_lang = src_lang
    tokenizer.tgt_lang = tgt_lang
    
    # Preprocess the text
    inputs = tokenizer(text, return_tensors="pt")
    # Generate translation
    translated_tokens = model.generate(**inputs, forced_bos_token_id=tokenizer.get_lang_id(tgt_lang))
    # Decode the translated text
    translated_text = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
    return translated_text


with open("translated_questions.txt", "w") as f:

    for idx, (question, options) in enumerate(all_questions_and_options):
        print(f" {idx + 1}: {translate(question)}\n")
        f.write(f" {idx + 1}: {translate(question)}\n")
        for i in range(0,len(options),2):
            x = ""
            if (type(options[i]) == str):
                x = f" {chr(97 + i)}) {translate(options[i])} "
            else:
                x = f" {chr(97 + i)}) {options[i]} "
            y = ""
            if (type(options[i+1]) == str):
                y = f" {chr(97 + i+1)}) {translate(options[i+1])} "
            else:
                y = f" {chr(97 + i+1)}) {translate(options[i+1])} "
            f.write(x+"    " + y + "\n")

        print()
        print(f"{question}")
        f.write(f"{question}\n")
        for i in range(0,len(options),2):
            x = f" {chr(97 + i)}) {options[i]} "
            y = f" {chr(97 + i+1)}) {translate(options[i+1])} "
            f.write(x+"    " + y + "\n")
        print()
        if idx == 40 :
            break;