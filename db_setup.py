from db import add_game

def setup_db():
    add_game("wordle", "1373389382551080992")
    add_game("timeguessr", "1373285606976917618")
    add_game("framed", "1373622523027259457")
    add_game("angle", "1373626933392179260")
    add_game("worldle", "1374710356424785962")
    add_game("hexle", "1374712040643498045")

if __name__ == "__main__":
    setup_db() 