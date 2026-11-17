import argparse
import uvicorn

def main():
    parser=argparse.ArgumentParser(description="Harvey Local sales workspace")
    parser.add_argument('--port',type=int,default=8000)
    args=parser.parse_args()
    uvicorn.run('local_sales.app:app',host='127.0.0.1',port=args.port,workers=1)

if __name__=='__main__':
    main()
