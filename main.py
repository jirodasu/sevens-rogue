import pyxel
import random

W,H=240,320
SUITS=['S','H','D','C']
SUIT_COL=[7,8,10,11]
RANKS=list(range(1,14))
RN={1:'A',11:'J',12:'Q',13:'K'}

class Game:
 def __init__(self):
  pyxel.init(W,H,title='SEVENS ROGUE',fps=30)
  self.reset(); pyxel.run(self.update,self.draw)
 def reset(self):
  self.rng=random.Random(17); self.turn=1; self.score=0; self.mult=1; self.done=False; self.msg='Choose a card or HOLD'
  self.lo={s:7 for s in SUITS}; self.hi={s:7 for s in SUITS}
  deck=[(s,r) for s in SUITS for r in RANKS if r!=7]; self.rng.shuffle(deck); self.deck=deck
  self.hand=[]; self.hold=[]; self.fire={}; self.bonus={}; self.last=False
  for _ in range(5): self.draw_card()
  self.roll_bonus()
 def draw_card(self):
  if not self.deck:return
  c=self.deck.pop(); self.hand.append(c)
  if self.rng.random()<.32:
   self.fire[c]=[self.rng.randint(2,4),self.rng.choice([20,30,40,50])]
 def playable(self,c):
  s,r=c; return r==self.lo[s]-1 or r==self.hi[s]+1
 def side(self,c):
  s,r=c
  if r==self.lo[s]-1:return (s,'L')
  if r==self.hi[s]+1:return (s,'R')
  return None
 def roll_bonus(self):
  self.bonus={}
  dirs=[(s,d) for s in SUITS for d in 'LR']; self.rng.shuffle(dirs)
  n=3 if self.last else 2
  kinds=['G30','G50','X2','CHEST'] if not self.last else ['G50','G80','X2','X3','CHEST']
  for k in dirs[:n]: self.bonus[k]=self.rng.choice(kinds)
 def apply_bonus(self,key):
  b=self.bonus.get(key)
  if not b:return ''
  if b[0]=='G':
   v=int(b[1:]); self.score+=v*self.mult; return f' +{v*self.mult}'
  if b[0]=='X':
   v=int(b[1:]); self.mult=min(9,self.mult*v); return f' x{v}'
  v=self.rng.choice([30,50,70]); self.score+=v*self.mult; return f' CHEST+{v*self.mult}'
 def play(self,i):
  if self.done or i>=len(self.hand):return
  c=self.hand[i]
  if not self.playable(c): self.msg='Blocked: open adjacent rank first'; return
  key=self.side(c); s,r=c
  if r<7:self.lo[s]=r
  else:self.hi[s]=r
  gain=10*self.mult; self.score+=gain; extra=''
  if c in self.fire:
   t,v=self.fire.pop(c)
   if t>0:self.score+=v*self.mult; extra+=f' FIRE+{v*self.mult}'
  extra+=self.apply_bonus(key)
  self.hand.pop(i); self.msg=f'{s}{RN.get(r,r)} +{gain}{extra}'
  self.draw_card(); self.advance()
 def hold_card(self,i):
  if self.done or i>=len(self.hand):return
  if len(self.hold)>=2:self.msg='HOLD is full';return
  c=self.hand.pop(i); self.hold.append(c); self.draw_card(); self.msg=f'Held {c[0]}{RN.get(c[1],c[1])}'; self.advance()
 def swap_hold(self,i):
  if self.done or i>=len(self.hold):return
  if len(self.hand)>=5:self.msg='Hand full: play/hold first';return
  self.hand.append(self.hold.pop(i)); self.msg='Returned from HOLD'
 def advance(self):
  for c in list(self.fire):
   self.fire[c][0]-=1
   if self.fire[c][0]<=0:self.fire.pop(c,None)
  self.turn+=1
  if self.turn==16:
   self.last=True; self.roll_bonus(); self.msg+=' | LAST RUSH!'
  elif self.turn<=20 and self.turn%3==1:self.roll_bonus()
  if self.turn>20:
   self.done=True; self.msg='CLEAR!' if self.score>=450 else 'RUN OVER'
 def update(self):
  if self.done:
   if pyxel.btnp(pyxel.KEY_R) or (pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and 70<pyxel.mouse_x<170 and 270<pyxel.mouse_y<300): self.reset()
   return
  if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
   x,y=pyxel.mouse_x,pyxel.mouse_y
   for i in range(len(self.hand)):
    bx=7+i*46
    if bx<=x<bx+42 and 226<=y<276:
     if y>=261:self.hold_card(i)
     else:self.play(i)
     return
   for i in range(len(self.hold)):
    bx=75+i*48
    if bx<=x<bx+42 and 282<=y<314:self.swap_hold(i);return
  for i,k in enumerate([pyxel.KEY_1,pyxel.KEY_2,pyxel.KEY_3,pyxel.KEY_4,pyxel.KEY_5]):
   if pyxel.btnp(k):
    if pyxel.btn(pyxel.KEY_SHIFT):self.hold_card(i)
    else:self.play(i)
  if pyxel.btnp(pyxel.KEY_Q):self.swap_hold(0)
  if pyxel.btnp(pyxel.KEY_W):self.swap_hold(1)
 def label(self,c):
  s,r=c; return s+str(RN.get(r,r))
 def draw(self):
  pyxel.cls(1)
  pyxel.text(7,6,'SEVENS ROGUE v0.1',7)
  pyxel.text(7,17,f'TURN {min(self.turn,20)}/20',10 if self.last else 6)
  pyxel.text(93,17,f'SCORE {self.score}',7); pyxel.text(185,17,f'x{self.mult}',10)
  if self.last:pyxel.text(88,29,'*** LAST RUSH ***',8)
  y0=43
  for si,s in enumerate(SUITS):
   y=y0+si*38; col=SUIT_COL[si]
   pyxel.text(5,y+9,s,col)
   for r in RANKS:
    x=18+(r-1)*16
    opened=self.lo[s]<=r<=self.hi[s]
    if r==7:
     pyxel.rect(x,y,14,22,col); pyxel.text(x+5,y+8,'7',0)
    elif opened:
     pyxel.rectb(x,y,14,22,col); pyxel.text(x+4,y+8,str(RN.get(r,r)),col)
    else:
     pyxel.rectb(x,y,14,22,5); pyxel.text(x+4,y+8,str(RN.get(r,r)),5)
   for d,xx in [('L',18),('R',18+12*16)]:
    b=self.bonus.get((s,d))
    if b:
     pyxel.text(xx,y+25,('<'+b) if d=='L' else (b+'>'),10 if self.last else 9)
  pyxel.line(5,201,235,201,5)
  pyxel.text(7,205,self.msg[:38],7)
  pyxel.text(7,216,'HAND: tap card=PLAY / bottom=HOLD',6)
  for i,c in enumerate(self.hand):
   x=7+i*46; good=self.playable(c)
   pyxel.rect(x,226,42,50,3 if good else 0); pyxel.rectb(x,226,42,50,11 if good else 5)
   pyxel.text(x+4,231,self.label(c),SUIT_COL[SUITS.index(c[0])])
   if c in self.fire:
    t,v=self.fire[c]; pyxel.text(x+3,244,f'F{t}+{v}',10)
   pyxel.line(x,260,x+41,260,5); pyxel.text(x+10,265,'HOLD',6)
  pyxel.text(7,282,'HOLD',6)
  for i,c in enumerate(self.hold):
   x=75+i*48; pyxel.rect(x,280,42,32,0);pyxel.rectb(x,280,42,32,6)
   pyxel.text(x+5,291,self.label(c),SUIT_COL[SUITS.index(c[0])])
  if self.done:
   pyxel.rect(35,92,170,105,0);pyxel.rectb(35,92,170,105,7)
   pyxel.text(88,110,'CLEAR!' if self.score>=450 else 'RUN OVER',11 if self.score>=450 else 8)
   pyxel.text(76,130,f'FINAL SCORE {self.score}',7)
   pyxel.text(69,145,'TARGET 450',6)
   pyxel.text(66,165,'Tap bottom / R retry',10)
   pyxel.rectb(70,270,100,30,10);pyxel.text(104,282,'RETRY',10)

Game()
