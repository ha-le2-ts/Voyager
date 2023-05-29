async def alice (
    customer_interface , # environment that uses code as action space
    planning_agent , # curriculum agent for proposing the next task
    action_agent , # action agent for code generation
    critic_agent , # critic agent for self - verification
    skill_manager , # skill manager for adding new skills and skill
    new_interaction_or_interval, # await for new interaction
    retrieval,
    training_mode:bool=False,
    max_retries: int = 4
    ) :
    # latest prompt, settings etc. based on all customer interactions
    agent_state = planning_agent.get_latest_agent_state()
    while True :
        # await until new interaction, web-socket style
        new_interaction = new_interaction_or_interval.receive()
        # critique upon receiving new interaction
        success , critique = critic_agent.check_interaction_success (
                new_interaction, interaction , agent_state
            )
        # Learning mind
        if success:
            skill_manager.add_skill ( script, critique )
            planning_agent.add_successful_interaction ( interaction,critique ) # last interaction 
        else :
            planning_agent.add_failed_interaction ( interaction, critique)  # last interaction 

        customer_state = (
            # Reflective & update customer style
            planning_agent.get_customer_state (
                planning_agent.get_customer_persona () ,
                planning_agent.get_customer_mind_state () ,
                planning_agent.get_successful_interactions () ,
                planning_agent.get_failed_interactions () ,
                new_interaction,
            )
        )
        passed = False
        # starting set-plan-critique-action loop
        while True:
            interaction = planning_agent.propose_next_interaction (
                agent_state , customer_state
            )

            script = None
            execution_errors = None
            critique = None
            success = False
            # try at most 4 rounds then 
            for i in range (max_retries) :
                skills = skill_manager.retrieve_skills (
                    interaction , critique
                )
                script = action_agent.generate_interaction_script(
                    interaction ,
                    script ,
                    execution_errors ,
                    critique ,
                    skills ,
                )
            
                # critique prior to apply to customers
                passed , critique = critic_agent.check_interaction_quality (
                        interaction , agent_state
                    )
                if passed or training_mode:
                    (
                        agent_state ,
                        execution_errors ,
                    ) = await customer_interface.interact(script) # handling back-forth interaction & update script mid-conversation
                    break
            if not execution_errors and passed:
                # action executed - return to waiting new interaction
                break
            # action failed to execute or cannot pass critic, try new interaction

                
            
                
            
            

        
        
        