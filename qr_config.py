class QRConfig:

    Sizes = {
        1 : {width:21,height:21}
    }

    Err_corr_lvls = {
        "LOW":[7,0,0],
        "MEDIUM":[15,0,1],
        "QUARTERLY":[25,1,0],
        "HIGH":[30,1,1]
    }

    
    
    def __init__(self):
        self.data=""
        self.modules=[];
        self.dataType=""
        self.color=""
        self.colorType="solid"
        self.backgroundColor=""
        self.err_corr_mode=Err_Corr_Mode.LOW
        self.mask_pattern=""

    
