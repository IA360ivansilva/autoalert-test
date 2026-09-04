import sys, subprocess, os
from mlx_audio.tts.generate import generate_audio
generate_audio(
    text="Carlos Mendes — nosso sistema mostra que seu 2024 Kia Sportage pode estar em boa posição de troca, com valor estimado perto de $18,400. Essa é a estimativa. O número real vem de uma avaliação de vinte minutos, sem compromisso. Traga o 2024 Kia Sportage na loja e um especialista confere estado, pneus e histórico. Se não estiver bom, você fica com o carro. Meu nome é Ivan, da Phil Smith Kia. Pode me ligar ou mandar mensagem no (954) 860-0537. Mensagem preparada pelo assistente de IA do Ivan.",
    model="mlx-community/Fun-CosyVoice3-0.5B-2512-fp16",
    ref_audio="/var/folders/6b/x1k01zcs249bmt5r70jrsr180000gp/T/tmpantnm7l0.wav",
    ref_text="Eu sou o Ivan, da Phil Smith Kia, aqui para te ajudar com sua troca de carro.",
    stt_model=None,
    language="Portuguese",
    file_prefix=os.path.splitext("/Users/clawbotlocal/autoalert-pages/kai_test/audios/ivan-test-male.mp3")[0],
    audio_format="wav",
)
wav = os.path.splitext("/Users/clawbotlocal/autoalert-pages/kai_test/audios/ivan-test-male.mp3")[0] + "_000.wav"
if os.path.isfile(wav):
    subprocess.run(["ffmpeg","-y","-i",wav,"-ar","24000","-b:a","72k","/Users/clawbotlocal/autoalert-pages/kai_test/audios/ivan-test-male.mp3"],
                   capture_output=True, timeout=120)
    os.remove(wav)
