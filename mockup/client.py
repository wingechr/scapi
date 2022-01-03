
class api:
    
    class mod:
        
        @staticmethod
        def fun(data: int, b: int, c: bool=None, d: int=None) -> int:
            """Example description
            multiline text
            
            Args:
                data(int): TODO: description
                b(int): TODO: description
                c(bool): TODO: description
                d(int): TODO: description
            
            Returns:
                int
            """
            request(
                "POST",
                "mod/fun/%s" % (b),
                params={"c": c, "d": d},
                data=encode(data)
            )