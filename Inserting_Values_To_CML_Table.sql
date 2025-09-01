USE [CLM]
GO

INSERT INTO [dbo].[CLM_Table]
           ([SR NO]
           ,[Certificate Name]
           ,[Issued To]
           ,[Issued By]
           ,[Domain]
           ,[Issuing Date]
           ,[Expire Date]
           ,[Type]
           ,[Owner]
           ,[Owner Contact Details]
           ,[Comment]
           ,[Issued]
           ,[Active])
     VALUES
           (2
           ,'efgh.google.com'
           ,'devanshugrwl@gmail.com'
           ,'Security Team'
           ,'Internal'
           ,'8/8/2023'
           ,'7/8/2026' 
           ,'Internal Certificate'
           ,'devanshugrwl@gmail.com'
           ,'-'
           ,'REQ0054116'
           ,'Issued'
           ,'Yes'
           )
           ,(3
           ,'ijkl.google.com'
           ,'devanshugrwl@gmail.com'
           ,'Security Team'
           ,'Internal'
           ,'8/8/2023'
           ,'7/8/2024' 
           ,'Internal Certificate'
           ,'devanshugrwl@gmail.com'
           ,'-'
           ,'REQ0054116'
           ,'Issued'
           ,'Yes'
           )
           ,(4
           ,'mnop.google.com'
           ,'devanshugrwl@gmail.com'
           ,'Security Team'
           ,'Internal'
           ,'8/8/2023'
           ,'7/8/2024' 
           ,'Internal Certificate'
           ,'devanshugrwl@gmail.com'
           ,'-'
           ,'REQ0054116'
           ,'Issued'
           ,'Yes'
           )
           ,(5
           ,'CN = qrst.google.com | SAN = DNS Name = qrst.google.com, DNS Name = uvwx-ec-01.google.com, DNS Name = uvwx-ec-02.google.com'
           ,'devanshugrwl@gmail.com'
           ,'Security Team'
           ,'Internal'
           ,'8/17/2024'
           ,'8/16/2025' 
           ,'Internal Certificate'
           ,'devanshugrwl@gmail.com'
           ,'-'
           ,'REQ0054133'
           ,'Issued'
           ,'Yes'
           )
           ,(6
           ,'CN = yzab.google.com | SAN = DNS Name = yzab.google.com, DNS Name = cdef-ee-02.google.com, DNS Name = cdef-ee-01.google.com, DNS Name = google.com'
           ,'devanshugrwl@gmail.com'
           ,'Security Team'
           ,'Internal'
           ,'8/17/2024'
           ,'8/16/2025' 
           ,'Internal Certificate'
           ,'devanshugrwl@gmail.com'
           ,'-'
           ,'REQ0054133'
           ,'Issued'
           ,'Yes'
           )
GO


